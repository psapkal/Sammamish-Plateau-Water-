import arcpy
import os
import json
from typing import Dict, Any, Optional


def loadConfig() -> Dict[str, Any]:
    """
    Load configuration from config.json file.
    
    Returns:
        Dictionary containing myDatabase configuration
        
    Raises:
        RuntimeError: If config file cannot be loaded
    """
    try:
        configPath = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(configPath, 'r') as configFile:
            config = json.load(configFile)
        
        if 'myDatabase' not in config:
            # Return empty dict if section doesn't exist
            return {}
            
        return config['myDatabase']
        
    except FileNotFoundError:
        print(f"Warning: Config file not found: {configPath}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Warning: Invalid JSON in config file: {str(e)}")
        return {}
    except Exception as e:
        print(f"Warning: Failed to load configuration: {str(e)}")
        return {}


class mydatabase:
    """
    Database maintenance class for ArcGIS Enterprise Geodatabases.
    
    This class provides comprehensive database maintenance functionality including:
    - Connection management (accepting/blocking connections)
    - User disconnection for maintenance windows
    - Database compression to reclaim space
    - Index rebuilding for optimal query performance
    - Dataset analysis for query optimizer statistics
    
    Attributes:
        databasepath (str): Path to the geodatabase for maintenance operations
    """
    
    def __init__(self, database: str):
        """
        Initialize the database maintenance object.
        
        Args:
            database (str): Path to the geodatabase (SDE connection file or file geodatabase)
        """
        self.databasepath = database

    def databasepath(self, databasepath: str) -> str:
        """
        Get the current database path.
        
        Args:
            databasepath (str): Database path
            
        Returns:
            str: The database path
        """
        return databasepath
    
    def tunedb(self) -> bool:
        """
        Perform comprehensive database maintenance operations.
        
        This method executes a complete database maintenance routine:
        1. Blocks new connections to prevent interference
        2. Disconnects all current users
        3. Compresses the database to reclaim space
        4. Re-enables connections
        5. Rebuilds indexes for optimal performance
        6. Analyzes datasets to update query optimizer statistics
        
        Returns:
            bool: True if all operations completed successfully, False otherwise
        """
        try:
            # Step 1: Block new connections during maintenance
            print("Blocking new database connections...")
            arcpy.AcceptConnections(self.databasepath, False)
            
            # Step 2: Disconnect all current users
            print("Disconnecting all users...")
            arcpy.DisconnectUser(self.databasepath, "ALL")
            
            # Step 3: Compress database to reclaim space and improve performance
            print("Starting database compression...")
            arcpy.Compress_management(self.databasepath)
            print("Database compression completed")
            
            # Step 4: Re-enable connections
            print("Re-enabling database connections...")
            arcpy.AcceptConnections(self.databasepath, True)
            
            # Step 5: Rebuild indexes for optimal query performance
            print("Starting index rebuild...")
            arcpy.RebuildIndexes_management(self.databasepath, "SYSTEM", "", "ALL")
            print("Index rebuild completed")
            
            # Step 6: Analyze datasets to update query optimizer statistics
            print("Starting dataset analysis...")
            arcpy.AnalyzeDatasets_management(
                self.databasepath, 
                "SYSTEM", 
                "", 
                "ANALYZE_BASE", 
                "ANALYZE_DELTA", 
                "ANALYZE_ARCHIVE"
            )
            print("Dataset analysis completed")
            
            print("Database maintenance completed successfully!")
            return True
            
        except Exception as e:
            print(f"Error during database maintenance: {str(e)}")
            # Ensure connections are re-enabled even if maintenance fails
            try:
                arcpy.AcceptConnections(self.databasepath, True)
                print("Database connections re-enabled after error")
            except:
                print("Warning: Could not re-enable database connections")
            return False
