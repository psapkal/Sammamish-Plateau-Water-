# Standard library imports
import arcpy
import json
import os

def loadConfig():
    """Load configuration from config.json file.

    Returns:
        dict: Configuration dictionary containing all application settings.

    Raises:
        FileNotFoundError: If config.json file is not found.
        json.JSONDecodeError: If config.json contains invalid JSON.
    """
    # Get the directory where this script is located
    scriptDir = os.path.dirname(os.path.abspath(__file__))
    configPath = os.path.join(scriptDir, 'config.json')

    try:
        with open(configPath, 'r') as configFile:
            config = json.load(configFile)
        return config
    except FileNotFoundError:
        print(f"Config file not found at: {configPath}")
        raise
    except json.JSONDecodeError as e:
        print(f"Error parsing config file: {e}")
        raise


def Model():
    """
    Main processing function for updating project tables in ArcGIS Online.

    This function performs the complete workflow for synchronizing Eden database
    project data with ArcGIS Online feature services. It handles both CIP and DEA
    project types through a standardized process:

    1. Portal authentication using configured credentials
    2. Loading configuration settings for data sources and workspace
    3. Creating filtered table views from Eden database views
    4. Truncating existing data in ArcGIS Online feature services
    5. Appending fresh data from database to feature services

    Raises:
        arcpy.ExecuteError: If any ArcGIS geoprocessing operation fails
        Exception: If portal authentication or configuration loading fails
    """
    # Load configuration settings from external JSON file
    # Load configuration settings from external JSON file
    config = loadConfig()
    updateConfig = config['updateProjectTables']

    # Sign in to portal
    arcpy.SignInToPortal(
        updateConfig['portalUrl'],
        updateConfig['username'],
        updateConfig['password']
    )
    
    # Configure ArcGIS environment settings
    # Set to False to prevent accidental overwrites during processing
    arcpy.env.overwriteOutput = False

    # Load data source configurations
    edenCipProjectsView = updateConfig['edenCipProjectsView']
    cipProjectsServiceUrl = updateConfig['cipProjectsServiceUrl']
    edenDeaProjectsView = updateConfig['edenDeaProjectsView']
    deaProjectsServiceUrl = updateConfig['deaProjectsServiceUrl']

    # Load workspace configuration for ArcGIS environment management
    # These paths define where temporary data processing and operations occur
    workspaceConfig = updateConfig['workspaceSettings']
    scratchWorkspacePath = workspaceConfig['scratchWorkspace']
    workspacePath = workspaceConfig['workspace']

    # Load table view and field configuration settings
    # These control data presentation and field visibility in the output
    cipProjectsTableView = updateConfig['tableView']
    projectFieldInfo = updateConfig['fieldInfo']

    # ========== CIP (Capital Improvement Projects) Processing ==========

    # Step 1: Create a filtered table view from Eden database CIP projects
    # This creates a temporary view with configured field visibility for inspection reports
    with arcpy.EnvManager(scratchWorkspace=scratchWorkspacePath, workspace=workspacePath):
        arcpy.management.MakeTableView(
            in_table=edenCipProjectsView,
            out_view=cipProjectsTableView,
            where_clause="",
            workspace="",
            field_info=projectFieldInfo
        )

    # Step 2: Clear existing CIP data from ArcGIS Online feature service
    # This ensures we start with a clean slate before loading current data
    truncatedCipTable = arcpy.management.TruncateTable(in_table=cipProjectsServiceUrl)[0]

    # Load fresh CIP projects data into the service table
    appendedCipTable = arcpy.management.Append(
        inputs=[cipProjectsTableView],
        target=truncatedCipTable,
        schema_type="TEST_AND_SKIP",
        field_mapping="",
        subtype="",
        expression=""
    )[0]

    # ========== DEA (Development Engineering Applications) Processing ==========

    # Step 1: Create a filtered table view from Eden database DEA projects
    # This creates a temporary view with configured field visibility for inspection reports
    deaProjectsTableView = updateConfig['deaTableView']  # Name for temporary DEA table view
    with arcpy.EnvManager(scratchWorkspace=scratchWorkspacePath, workspace=workspacePath):
        arcpy.management.MakeTableView(
            in_table=edenDeaProjectsView,
            out_view=deaProjectsTableView,
            where_clause="",
            workspace="",
            field_info=projectFieldInfo
        )

    # Step 2: Clear existing DEA data from ArcGIS Online feature service
    # This ensures we start with a clean slate before loading current data
    truncatedDeaTable = arcpy.management.TruncateTable(in_table=deaProjectsServiceUrl)[0]

    # Step 3: Append fresh DEA projects data to the ArcGIS Online service
    # This loads all current DEA projects from the database into the feature service
    appendedDeaTable = arcpy.management.Append(
        inputs=[deaProjectsTableView],
        target=truncatedDeaTable,
        schema_type="TEST_AND_SKIP",
        field_mapping="",
        subtype="",
        expression=""
    )[0]

if __name__ == '__main__':
    """
    Main execution block when script is run directly.

    This block executes when the script is run as a standalone program.
    It configures the global ArcGIS environment using settings from the
    configuration file and then executes the main processing workflow.

    The EnvManager context ensures that all ArcGIS operations throughout
    the script use consistent workspace and scratch workspace settings.
    """
    # Load configuration settings for global environment setup
    config = loadConfig()
    updateConfig = config['updateProjectTables']
    workspaceConfig = updateConfig['workspaceSettings']

    # Configure global ArcGIS environment using settings from config file
    # EnvManager ensures consistent workspace settings for all geoprocessing operations
    with arcpy.EnvManager(
        scratchWorkspace=workspaceConfig['scratchWorkspace'],
        workspace=workspaceConfig['workspace']
    ):
        # Execute the complete project table update workflow
        Model()
