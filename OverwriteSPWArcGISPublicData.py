# Standard library imports
import arcpy
import os
import sys
import json
from arcgis.gis import GIS
from typing import Optional, Tuple

def loadConfig() -> dict:
    """
    Load configuration from config.json file.
    
    Returns:
        dict: Configuration dictionary containing all application settings
        
    Raises:
        FileNotFoundError: If config.json file is not found
        json.JSONDecodeError: If config.json contains invalid JSON
    """
    scriptDir = os.path.dirname(os.path.abspath(__file__))
    configPath = os.path.join(scriptDir, 'config.json')
    
    try:
        with open(configPath, 'r') as configFile:
            config = json.load(configFile)
        return config['overwriteSPWArcGISPublicData']
    except FileNotFoundError:
        print(f"Config file not found at: {configPath}")
        raise
    except json.JSONDecodeError as e:
        print(f"Error parsing config file: {e}")
        raise

def validatePaths(prjPath: str, relPath: str) -> bool:
    """
    Validate that required file paths exist and are accessible.
    
    Args:
        prjPath (str): Path to the ArcGIS Pro project file
        relPath (str): Path to the temporary directory
        
    Returns:
        bool: True if all paths are valid
        
    Raises:
        FileNotFoundError: If required paths don't exist
    """
    if not os.path.exists(prjPath):
        raise FileNotFoundError(f"Project file not found: {prjPath}")
    
    if not os.path.exists(relPath):
        print(f"Creating temporary directory: {relPath}")
        os.makedirs(relPath, exist_ok=True)
    
    return True

def analyzeProjectLayers(prj) -> None:
    """
    Analyze project layers and report broken data sources.
    
    Args:
        prj: ArcGIS Pro project object
    """
    print("\n=== Project Layer Analysis ===")
    
    for map in prj.listMaps():
        print(f"Map: {map.name} Layers")
        
        for lyr in map.listLayers():
            if lyr.isBroken:
                print(f"(BROKEN) {lyr.name}")
            else:
                print(f"{lyr.name}")

def createServiceDefinition(prj, map, sddraft: str, sd: str, sdFsName: str) -> None:
    """
    Create and stage a service definition from the ArcGIS Pro map.
    
    Args:
        prj: ArcGIS Pro project object
        map: Map object to publish
        sddraft (str): Path for service definition draft file
        sd (str): Path for staged service definition file
        sdFsName (str): Name for the feature service
    """
    print("Creating service definition...")
    
    # Create service definition draft
    arcpy.mp.CreateWebLayerSDDraft(
        map, 
        sddraft, 
        sdFsName, 
        'MY_HOSTED_SERVICES', 
        'FEATURE_ACCESS',
        '', 
        True,  # Enable feature access
        True   # Allow exports
    )
    
    # Stage the service definition
    arcpy.StageService_server(sddraft, sd)
    print(f"Service definition created: {sd}")

def configureSharing(featureService, shareWithOrg: bool, shareWithEveryone: bool, shareWithGroups: bool):
    """
    Configure sharing settings for a feature service.
    
    Args:
        featureService: The feature service item to configure sharing for
        shareWithOrg: Whether to share with the organization
        shareWithEveryone: Whether to share with everyone (public)
        shareWithGroups: Whether to share with specific groups
    
    Raises:
        RuntimeError: If sharing configuration fails
    """
    try:
        if shareWithOrg or shareWithEveryone or shareWithGroups:
            print("Setting sharing options...")
            featureService.share(org=shareWithOrg, everyone=shareWithEveryone, groups=shareWithGroups)
            print("Sharing options configured successfully")
        else:
            print("No sharing options specified - service remains private")
            
    except Exception as e:
        raise RuntimeError(f"Failed to configure sharing: {str(e)}")


def updateServiceDefinition(serviceItem, sdFilePath: str):
    """
    Update an existing service definition item with new data and publish with overwrite.
    
    Args:
        serviceItem: The service definition item to update
        sdFilePath: Path to the new service definition file (.sd)
    
    Returns:
        Feature service item that was published
    
    Raises:
        RuntimeError: If update or publish operation fails
    """
    try:
        print("Uploading and overwriting service definition...")
        
        # Update the service definition item with new data
        serviceItem.update(data=sdFilePath)
        
        print("Overwriting existing feature service...")
        
        # Publish with overwrite to replace existing service
        featureService = serviceItem.publish(overwrite=True)
        
        print(f"Successfully updated feature service: {featureService.title} (ID: {featureService.id})")
        
        return featureService
        
    except Exception as e:
        raise RuntimeError(f"Failed to update service definition: {str(e)}")


def findExistingService(gis: GIS, serviceName: str, username: str):
    """
    Find an existing service definition item on ArcGIS Online.
    
    Args:
        gis: Authenticated GIS connection object
        serviceName: Name of the service to search for
        username: Username to filter by (owner)
    
    Returns:
        ContentItem object representing the found service definition
    
    Raises:
        RuntimeError: If service definition is not found
    """
    try:
        print("Searching for original service definition on portal...")
        
        # Search for service definition by name and owner
        searchQuery = f"{serviceName} AND owner:{username}"
        searchResults = gis.content.search(query=searchQuery, item_type="Service Definition")
        
        if not searchResults:
            raise RuntimeError(f"No service definition found with name '{serviceName}' owned by '{username}'")
        
        serviceItem = searchResults[0]
        print(f"Found service definition: {serviceItem.title} (ID: {serviceItem.id})")
        
        return serviceItem
        
    except Exception as e:
        raise RuntimeError(f"Failed to find existing service: {str(e)}")


def connectToPortal(portalUrl: str, username: str, password: str) -> GIS:
    """
    Connect to ArcGIS Online portal.
    
    Args:
        portalUrl (str): Portal URL
        username (str): Username for authentication
        password (str): Password for authentication
        
    Returns:
        GIS: Connected GIS object
        
    Raises:
        Exception: If connection fails
    """
    print(f"Connecting to {portalUrl}...")
    
    try:
        gis = GIS(portalUrl, username, password)
        print(f"Connected as: {gis.users.me.username}")
        return gis
    except Exception as e:
        print(f"Failed to connect to portal: {e}")
        raise

def main():
    """
    Main execution function that orchestrates the complete workflow.
    """
    try:
        # Load configuration
        config = loadConfig()
        
        # Extract configuration values
        projectPath = config['projectPath']
        mapName = config['mapName']
        serviceName = config['serviceName']
        portalUrl = config['portalUrl']
        username = config['username']
        password = config['password']
        tempPath = config['tempPath']
        
        # Set sharing options from config
        shareWithOrg = config['sharing']['organization']
        shareWithEveryone = config['sharing']['everyone']
        shareWithGroups = config['sharing']['groups']
        
        # Create paths for service definition files
        sddraft = os.path.join(tempPath, "WebUpdate.sddraft")
        sd = os.path.join(tempPath, "WebUpdate.sd")
        
        print("Creating service definition file...")
        
        # Validate paths before processing
        validatePaths(projectPath, tempPath)
        
        # Configure ArcPy environment
        arcpy.env.overwriteOutput = True
        
        # Open project and get map
        prj = arcpy.mp.ArcGISProject(projectPath)
        m = prj.listMaps(mapName)[0]
        
        # Analyze project layers
        analyzeProjectLayers(prj)
        
        # Create service definition
        createServiceDefinition(prj, m, sddraft, sd, serviceName)
        
        # Connect to portal
        gis = connectToPortal(portalUrl, username, password)
        
        # Find existing service definition and update it
        serviceItem = findExistingService(gis, serviceName, username)
        
        # Update service definition and publish
        fs = updateServiceDefinition(serviceItem, sd)
        
        # Configure sharing settings
        configureSharing(fs, shareWithOrg, shareWithEveryone, shareWithGroups)
        
        print(f"Successfully completed update: {fs.title} (ID: {fs.id})")
        
    except Exception as e:
        print(f"Error in main execution: {str(e)}")
        raise


if __name__ == "__main__":
    main()
