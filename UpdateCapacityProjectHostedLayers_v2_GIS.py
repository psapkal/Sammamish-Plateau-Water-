import arcpy, os, time
from datetime import datetime, timedelta

## Start timer
startTime = time.time()

## Get date minus X number of hours
d = datetime.today() - timedelta(days=8)
date = d.date().strftime("%Y-%m-%d")

## variables
gdb = r"\\SPW-DC1\S_DIR\GIS\EnterpriseGISProjects\ESRI_I_I\Solution\CapacityProjectData.gdb"

viewLiftStations = r"\\SPW-DC1\S_DIR\GIS\EnterpriseGISProjects\ESRI_I_I\Solution\GISDB1.sde\reporting.dbo.view_SCADA_Liftstation_FlowToday_CAP"
viewLiftStationsInflow = r"\\SPW-DC1\S_DIR\GIS\EnterpriseGISProjects\ESRI_I_I\Solution\GISDB1.sde\reporting.dbo.view_SCADA_Liftstation_InFlowToday_CAP"
viewPrecipitation =  r"\\SPW-DC1\S_DIR\GIS\EnterpriseGISProjects\ESRI_I_I\Solution\GISDB1.sde\reporting.dbo.view_SCADA_Weather_RainToday_CAP"

liftStations = os.path.join(gdb, "LiftStations_Flow")
inliftStations = os.path.join(gdb, "LiftStations_Inflow")
precipitation = os.path.join(gdb, "WeatherStations_Precipitation")

SPW_Precipitation_Statistics = "WeatherStations_Precipitation_Statistics"
SPW_Liftstations_DissolveFlows = "Liftstations_DissolveFlows"

httpLiftStations = "https://gisweb.spwater.org/host/rest/services/Hosted/Capacity_Project/FeatureServer/2"
httpLiftStationsInflow = "https://gisweb.spwater.org/host/rest/services/Hosted/Capacity_Project/FeatureServer/1"
httpWeatherStations = "https://gisweb.spwater.org/host/rest/services/Hosted/Capacity_Project/FeatureServer/0"
httpDMA = "https://gisweb.spwater.org/host/rest/services/Hosted/Capacity_Project/FeatureServer/3"

## Process: Set workspace
arcpy.env.workspace = gdb
arcpy.env.overwriteOutput = 1

## Process: XYTableToPoint
print("converting liftstation and precipitation tables to point feature classes")
sr = arcpy.SpatialReference(6597)
arcpy.management.XYTableToPoint(viewLiftStations, liftStations, "X_COORD", "Y_COORD", None, sr)
arcpy.management.XYTableToPoint(viewLiftStationsInflow, inliftStations, "X_COORD", "Y_COORD", None, sr)
arcpy.management.XYTableToPoint(viewPrecipitation, precipitation, "X_COORD", "Y_COORD", None, sr)

print("calculating DMA_ID")
arcpy.management.CalculateField(liftStations, "dma_id", "!dma! + str(!EventDateTime!)", "PYTHON3", "", "TEXT")
arcpy.management.CalculateField(inliftStations, "dma_id", "!dma! + str(!EventDateTime!)", "PYTHON3", "", "TEXT")

print("joining lifstations by DMA_ID to inflow data and DMA details")
arcpy.management.JoinField(liftStations, "dma_id", inliftStations, "dma_id", "InFlowToday_Gallons")
##arcpy.management.JoinField(liftStations, "dma", httpDMA, "dma", ["uphill_dma", "SUM_max_capacity", "SUM_alert_80percentage", "SUM_alert_90percentage", "Area_Feet"])
arcpy.management.JoinField(liftStations, "dma", httpDMA, "dma", ["Area_Feet"])

arcpy.management.AddField(liftStations, "LOCAL_FlowToday_Gallons", "DOUBLE")
arcpy.management.AddField(liftStations, "LOCAL_InFlowToday_Gallons", "DOUBLE")
arcpy.management.AddField(liftStations, "MEAN_RainToday_Gallons", "DOUBLE")

## Create dictionary for uphill DMAs
uphillDMADict = {}

## Iterate through DMA feature class to find those that have uphill DMAs
with arcpy.da.SearchCursor(liftStations, ['uphill_dma', 'dma'], "uphill_dma <> 'None'") as cursor:
    for row in cursor:
        dmas = row[0].split(',')
        dmaList = []
        for dma in dmas:
            dma = dma.lstrip()
            dma = dma.rstrip()
            dmaList.append(dma)
        tupleDMAs = tuple(dmaList)
        uphillDMADict[row[1]] = tupleDMAs
del cursor

for key, val in uphillDMADict.items():
    print("\nProcessing {0}".format(key))

    if len(val) == 1:
        val = val[0]
        expression = "dma = '{0}'".format(val)
    else:
        expression = "dma in {0}".format(val)

    try:       
        arcpy.management.DeleteField(liftStations, ["SUM_FlowToday_Gallons", "SUM_InFlowToday_Gallons"])
    except:
        print ("NOPE")
        pass

    print(expression)
    
    ## Process: MakeFeatureLayer_management
    print("\tcreating Feature layer of uphill DMAs")
    arcpy.management.MakeFeatureLayer(liftStations, "dmaLyr", expression, gdb, "")

    ## Process: Dissolve
    print("\tdissolving dmalyr and summing flow")
    arcpy.management.Dissolve("dmaLyr", SPW_Liftstations_DissolveFlows, "EventDateTime", "FlowToday_Gallons SUM; InFlowToday_Gallons SUM", "MULTI_PART", "DISSOLVE_LINES")

    ## Process:
    print("\tjoining summed flows to liftstation and calculating uphill flows")
    arcpy.management.MakeFeatureLayer(liftStations, "dmaLiftStationsLyr", "dma = '{0}'".format(key))
    arcpy.management.JoinField("dmaLiftStationsLyr", "EventDateTime", SPW_Liftstations_DissolveFlows, "EventDateTime", "SUM_FlowToday_Gallons; SUM_InFlowToday_Gallons")
    arcpy.management.CalculateField("dmaLiftStationsLyr", "Uphill_Flow", "!SUM_FlowToday_Gallons!", "PYTHON3", "", "DOUBLE")
    arcpy.management.CalculateField("dmaLiftStationsLyr", "Uphill_InFlow", "!SUM_InFlowToday_Gallons!", "PYTHON3", "", "DOUBLE")
    
    ## Process: CalculateField
    print("\tcalculating flow difference")
    arcpy.management.CalculateField("dmaLiftStationsLyr", "LOCAL_FlowToday_Gallons", "!FlowToday_Gallons! - !Uphill_Flow!", "PYTHON3", "", "")
    arcpy.management.CalculateField("dmaLiftStationsLyr", "LOCAL_InFlowToday_Gallons", "!InFlowToday_Gallons! - !Uphill_InFlow!", "PYTHON3", "", "")

    arcpy.management.Delete("dmaLyr")
    arcpy.management.Delete(SPW_Liftstations_DissolveFlows)
    arcpy.management.Delete("dmaLiftStationsLyr")

print("statistics_analysis SPW_Precipitation_Statistics")
arcpy.Statistics_analysis(precipitation, SPW_Precipitation_Statistics, "RainToday MIN;RainToday MAX;RainToday MEAN", "EventDateTime")

print("joining precipitation and consumption stats to liftstation, calculating consumption gallons and precipication gallons")
arcpy.management.JoinField(liftStations, "EventDateTime", SPW_Precipitation_Statistics, "EventDateTime", "MEAN_RainToday")
##arcpy.management.CalculateField(liftStations, "MEAN_RainToday_Gallons", "((!Area_Feet!*144) * !MEAN_RainToday!)/231", "PYTHON_9.3", "", "")
arcpy.management.CalculateField(liftStations, "MEAN_RainToday_Gallons", "(!Area_Feet! * !MEAN_RainToday!)/231", "PYTHON_9.3", "", "")
##arcpy.management.CalculateField(liftStations, "MEAN_RainToday_Gallons", "!Area_Feet! * !MEAN_RainToday!/2312 *  0.623", "PYTHON_9.3", "", "")

## Process: MakeFeatureLayer_management
print("making feature layer")
arcpy.MakeFeatureLayer_management(httpLiftStations, "dmaLiftStations_Lyr", "EventDateTime > timestamp '{0}'".format(date))
arcpy.MakeFeatureLayer_management(httpLiftStationsInflow, "dmaLiftStationsInflow_Lyr", "EventDateTime > timestamp '{0}'".format(date))
arcpy.MakeFeatureLayer_management(httpWeatherStations, "precipidation_Lyr", "EventDateTime > timestamp '{0}'".format(date))

arcpy.MakeFeatureLayer_management(liftStations, "dmaLiftStations_Lyr2", "EventDateTime > timestamp '{0}'".format(date))
arcpy.MakeFeatureLayer_management(liftStations, "dmaLiftStationsInflow_Lyr2", "EventDateTime > timestamp '{0}'".format(date))
arcpy.MakeFeatureLayer_management(precipitation, "precipidation_Lyr2", "EventDateTime > timestamp '{0}'".format(date))

## Update timer
updateTime = time.time()

## Process: DeleteRows_management
print("deleting rows")
arcpy.DeleteRows_management("dmaLiftStations_Lyr")
arcpy.DeleteRows_management("dmaLiftStationsInflow_Lyr")
arcpy.DeleteRows_management("precipidation_Lyr")

## Process: Append
print("appending results")
arcpy.management.Append("dmaLiftStations_Lyr2", httpLiftStations, "NO_TEST", '', '', '')
arcpy.management.Append("dmaLiftStationsInflow_Lyr2", httpWeatherStations, "NO_TEST", '', '', '')
arcpy.management.Append("precipidation_Lyr2", httpLiftStationsInflow, "NO_TEST", '', '', '')

## Update Timer
endUpdateTime = time.time()
elapsedTime = round((endUpdateTime - updateTime) / 60, 2)
print("Update completed in {0} minutes".format(elapsedTime))

## End Timer
endTime = time.time()
elapsedTime = round((endTime - startTime) / 60, 2)
print("Script completed in {0} minutes".format(elapsedTime))

##exit(1)

