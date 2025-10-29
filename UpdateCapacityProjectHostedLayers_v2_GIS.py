import arcpy
import os
import time
import json
from datetime import datetime, timedelta


def loadConfig():
    """
    Load configuration from config.json file.

    Returns:
        dict: Configuration dictionary containing updateCapacityProjectHostedLayers settings

    Raises:
        RuntimeError: If config file cannot be loaded
    """
    try:
        configPath = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(configPath, 'r', encoding='utf-8') as configFile:
            config = json.load(configFile)
        return config['updateCapacityProjectHostedLayers']
    except Exception as e:
        raise RuntimeError(f"Failed to load config.json: {e}")


def initializeVariables(config):
    """
    Initialize all variables from configuration and calculate date.

    Args:
        config (dict): Configuration dictionary

    Returns:
        dict: Dictionary containing all initialized variables
    """
    # Get date minus 8 days
    d = datetime.today() - timedelta(days=8)
    date = d.date().strftime("%Y-%m-%d")

    # Database and workspace paths
    gdb = config['capacityProjectGdb']

    # View paths
    viewLiftStations = config['viewLiftStations']
    viewLiftStationsInflow = config['viewLiftStationsInflow']
    viewPrecipitation = config['viewPrecipitation']

    # Local feature class paths
    liftStations = os.path.join(gdb, "LiftStations_Flow")
    inliftStations = os.path.join(gdb, "LiftStations_Inflow")
    precipitation = os.path.join(gdb, "WeatherStations_Precipitation")

    # Temporary feature classes
    precipitationStats = config['precipitationStatistics']
    dissolveFlows = config['liftStationDissolveFlows']

    # HTTP service URLs
    httpLiftStations = config['httpLiftStations']
    httpLiftStationsInflow = config['httpLiftStationsInflow']
    httpWeatherStations = config['httpWeatherStations']
    httpDMA = config['httpDMA']

    return {
        'date': date,
        'gdb': gdb,
        'viewLiftStations': viewLiftStations,
        'viewLiftStationsInflow': viewLiftStationsInflow,
        'viewPrecipitation': viewPrecipitation,
        'liftStations': liftStations,
        'inliftStations': inliftStations,
        'precipitation': precipitation,
        'precipitationStats': precipitationStats,
        'dissolveFlows': dissolveFlows,
        'httpLiftStations': httpLiftStations,
        'httpLiftStationsInflow': httpLiftStationsInflow,
        'httpWeatherStations': httpWeatherStations,
        'httpDMA': httpDMA
    }


# Initialize variables
config = loadConfig()
vars_dict = initializeVariables(config)

## Start timer
startTime = time.time()


def setupWorkspace(gdb):
    """
    Set up ArcPy workspace environment.

    Args:
        gdb (str): Path to geodatabase
    """
    arcpy.env.workspace = gdb
    arcpy.env.overwriteOutput = 1


# Set up workspace
setupWorkspace(vars_dict['gdb'])


def createPointFeatureClasses(vars_dict):
    """
    Convert database views to point feature classes.

    Args:
        vars_dict (dict): Dictionary containing variable paths
    """
    print("Converting liftstation and precipitation tables to point feature classes")
    sr = arcpy.SpatialReference(6597)
    
    # Create point feature classes from XY tables
    arcpy.management.XYTableToPoint(vars_dict['viewLiftStations'], vars_dict['liftStations'], "X_COORD", "Y_COORD", None, sr)
    arcpy.management.XYTableToPoint(vars_dict['viewLiftStationsInflow'], vars_dict['inliftStations'], "X_COORD", "Y_COORD", None, sr)
    arcpy.management.XYTableToPoint(vars_dict['viewPrecipitation'], vars_dict['precipitation'], "X_COORD", "Y_COORD", None, sr)


# Create point feature classes
createPointFeatureClasses(vars_dict)


def calculateDMAIdsAndJoinData(vars_dict):
    """
    Calculate DMA IDs and join lift station data.

    Args:
        vars_dict (dict): Dictionary containing variable paths
    """
    print("Calculating DMA_ID")
    arcpy.management.CalculateField(vars_dict['liftStations'], "dma_id", "!dma! + str(!EventDateTime!)", "PYTHON3", "", "TEXT")
    arcpy.management.CalculateField(vars_dict['inliftStations'], "dma_id", "!dma! + str(!EventDateTime!)", "PYTHON3", "", "TEXT")

    print("Joining lift stations by DMA_ID to inflow data and DMA details")
    arcpy.management.JoinField(vars_dict['liftStations'], "dma_id", vars_dict['inliftStations'], "dma_id", "InFlowToday_Gallons")
    arcpy.management.JoinField(vars_dict['liftStations'], "dma", vars_dict['httpDMA'], "dma", ["Area_Feet"])

    # Add calculation fields
    arcpy.management.AddField(vars_dict['liftStations'], "LOCAL_FlowToday_Gallons", "DOUBLE")
    arcpy.management.AddField(vars_dict['liftStations'], "LOCAL_InFlowToday_Gallons", "DOUBLE")
    arcpy.management.AddField(vars_dict['liftStations'], "MEAN_RainToday_Gallons", "DOUBLE")


# Calculate DMA IDs and join data
calculateDMAIdsAndJoinData(vars_dict)


def processUphillDMAFlows(vars_dict):
    """
    Process uphill DMA flows for each DMA.

    Args:
        vars_dict (dict): Dictionary containing variable paths
    """
    # Create dictionary for uphill DMAs
    uphillDMADict = {}

    # Iterate through DMA feature class to find those that have uphill DMAs
    with arcpy.da.SearchCursor(vars_dict['liftStations'], ['uphill_dma', 'dma'], "uphill_dma <> 'None'") as cursor:
        for row in cursor:
            dmas = row[0].split(',')
            dmaList = []
            for dma in dmas:
                dma = dma.lstrip().rstrip()
                dmaList.append(dma)
            tupleDMAs = tuple(dmaList)
            uphillDMADict[row[1]] = tupleDMAs

    # Process each DMA with uphill flows
    for key, val in uphillDMADict.items():
        print(f"\nProcessing {key}")

        if len(val) == 1:
            val = val[0]
            expression = f"dma = '{val}'"
        else:
            expression = f"dma in {val}"

        try:
            arcpy.management.DeleteField(vars_dict['liftStations'], ["SUM_FlowToday_Gallons", "SUM_InFlowToday_Gallons"])
        except:
            print("No existing sum fields to delete")

        print(f"\t{expression}")

        # Create Feature layer of uphill DMAs
        print("\tCreating Feature layer of uphill DMAs")
        arcpy.management.MakeFeatureLayer(vars_dict['liftStations'], "dmaLyr", expression, vars_dict['gdb'], "")

        # Dissolve and sum flows
        print("\tDissolving dmalyr and summing flow")
        arcpy.management.Dissolve("dmaLyr", vars_dict['dissolveFlows'], "EventDateTime", 
                                 "FlowToday_Gallons SUM; InFlowToday_Gallons SUM", "MULTI_PART", "DISSOLVE_LINES")

        # Join summed flows and calculate uphill flows
        print("\tJoining summed flows to liftstation and calculating uphill flows")
        arcpy.management.MakeFeatureLayer(vars_dict['liftStations'], "dmaLiftStationsLyr", f"dma = '{key}'")
        arcpy.management.JoinField("dmaLiftStationsLyr", "EventDateTime", vars_dict['dissolveFlows'], 
                                  "EventDateTime", "SUM_FlowToday_Gallons; SUM_InFlowToday_Gallons")
        arcpy.management.CalculateField("dmaLiftStationsLyr", "Uphill_Flow", "!SUM_FlowToday_Gallons!", "PYTHON3", "", "DOUBLE")
        arcpy.management.CalculateField("dmaLiftStationsLyr", "Uphill_InFlow", "!SUM_InFlowToday_Gallons!", "PYTHON3", "", "DOUBLE")

        # Calculate flow differences
        print("\tCalculating flow difference")
        arcpy.management.CalculateField("dmaLiftStationsLyr", "LOCAL_FlowToday_Gallons", 
                                       "!FlowToday_Gallons! - !Uphill_Flow!", "PYTHON3", "", "")
        arcpy.management.CalculateField("dmaLiftStationsLyr", "LOCAL_InFlowToday_Gallons", 
                                       "!InFlowToday_Gallons! - !Uphill_InFlow!", "PYTHON3", "", "")

        # Clean up temporary layers
        arcpy.management.Delete("dmaLyr")
        arcpy.management.Delete(vars_dict['dissolveFlows'])
        arcpy.management.Delete("dmaLiftStationsLyr")


# Process uphill DMA flows
processUphillDMAFlows(vars_dict)


def calculatePrecipitationStatistics(vars_dict):
    """
    Calculate precipitation statistics and join to lift stations.

    Args:
        vars_dict (dict): Dictionary containing variable paths
    """
    print("Calculating precipitation statistics")
    arcpy.Statistics_analysis(vars_dict['precipitation'], vars_dict['precipitationStats'],
                             "RainToday MIN;RainToday MAX;RainToday MEAN", "EventDateTime")

    print("Joining precipitation stats to lift stations and calculating precipitation gallons")
    arcpy.management.JoinField(vars_dict['liftStations'], "EventDateTime", vars_dict['precipitationStats'],
                              "EventDateTime", "MEAN_RainToday")
    arcpy.management.CalculateField(vars_dict['liftStations'], "MEAN_RainToday_Gallons",
                                   "(!Area_Feet! * !MEAN_RainToday!)/231", "PYTHON3", "", "")


# Calculate precipitation statistics
calculatePrecipitationStatistics(vars_dict)


def updateHostedLayers(vars_dict):
    """
    Create feature layers, delete old data, and append new data to hosted layers.
    
    Args:
        vars_dict (dict): Dictionary containing variable paths

    Returns:
        float: Update start time for calculating elapsed time
    """
    # Create feature layers
    print("Making feature layers")

    # Create layers from hosted services (for deletion)
    arcpy.MakeFeatureLayer_management(vars_dict['httpLiftStations'], "dmaLiftStations_Lyr", 
                                     f"EventDateTime > timestamp '{vars_dict['date']}'")
    arcpy.MakeFeatureLayer_management(vars_dict['httpLiftStationsInflow'], "dmaLiftStationsInflow_Lyr", 
                                     f"EventDateTime > timestamp '{vars_dict['date']}'")
    arcpy.MakeFeatureLayer_management(vars_dict['httpWeatherStations'], "precipidation_Lyr", 
                                     f"EventDateTime > timestamp '{vars_dict['date']}'")

    # Create layers from local data (for appending)
    arcpy.MakeFeatureLayer_management(vars_dict['liftStations'], "dmaLiftStations_Lyr2", 
                                     f"EventDateTime > timestamp '{vars_dict['date']}'")
    arcpy.MakeFeatureLayer_management(vars_dict['liftStations'], "dmaLiftStationsInflow_Lyr2", 
                                     f"EventDateTime > timestamp '{vars_dict['date']}'")
    arcpy.MakeFeatureLayer_management(vars_dict['precipitation'], "precipidation_Lyr2", 
                                     f"EventDateTime > timestamp '{vars_dict['date']}'")

    # Update timer
    updateTime = time.time()

    # Delete old rows
    print("Deleting old rows")
    arcpy.DeleteRows_management("dmaLiftStations_Lyr")
    arcpy.DeleteRows_management("dmaLiftStationsInflow_Lyr")
    arcpy.DeleteRows_management("precipidation_Lyr")

    # Append new results
    print("Appending new results")
    arcpy.management.Append("dmaLiftStations_Lyr2", vars_dict['httpLiftStations'], "NO_TEST", '', '', '')
    arcpy.management.Append("dmaLiftStationsInflow_Lyr2", vars_dict['httpWeatherStations'], "NO_TEST", '', '', '')
    arcpy.management.Append("precipidation_Lyr2", vars_dict['httpLiftStationsInflow'], "NO_TEST", '', '', '')

    return updateTime


# Update hosted layers
updateTime = updateHostedLayers(vars_dict)

# Calculate and display timing results
endUpdateTime = time.time()
elapsedTime = round((endUpdateTime - updateTime) / 60, 2)
print(f"Update completed in {elapsedTime} minutes")

# End Timer
endTime = time.time()
totalElapsedTime = round((endTime - startTime) / 60, 2)
print(f"Script completed in {totalElapsedTime} minutes")

