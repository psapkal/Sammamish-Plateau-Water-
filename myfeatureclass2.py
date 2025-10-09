import arcpy


def loadConfig():
    """
    Load configuration from config.json file.
    
    Returns:
        dict: Configuration dictionary containing myFeatureClass settings
        
    Raises:
        RuntimeError: If config file cannot be loaded
    """
    try:
        configPath = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(configPath, 'r') as configFile:
            config = json.load(configFile)
        return config['myFeatureClass']
    except Exception as e:
        raise RuntimeError(f"Failed to load config.json: {e}")
class MyFeatureClass:
    def __init__(self, featureclass, config=None):
        """
        Initialize the feature class handler.
        """     
        desc = arcpy.Describe(featureclass)
        self.basename = desc.basename
        self.path = desc.path
        self.name = desc.name
        self.file = desc.file

        # Load configuration
        if config is None:
            self.config = loadConfig()
        else:
            self.config = config

    def validatefieldexists(self, in_field):
        """
        Check if a field exists in the feature class.
        
        Args:
            in_field (str): Name of the field to validate
            
        Returns:
            bool: True if field exists, False otherwise
        """
        in_field = arcpy.ListFields(self.basename, in_field)
        if len(in_field) != 1:
            return False
        else:
            return True
        
    def getmaxvalue(self, in_field):
        """
        Get the maximum value from a numeric field.
        
        Args:
            in_field (str): Name of the field to get max value from
            
        Returns:
            int/float: Maximum value in the field
        """
        values = [row[0] for row in arcpy.da.SearchCursor(self.basename, in_field)]
        uniqueValues = set(values)
        return max(uniqueValues)
    
    def updatenumberincrementbyfield(self, in_field):
        """
        Update null or empty fields with incrementally increasing numbers.
        
        Args:
            in_field (str): Name of the field to update
        """       
        if self.validatefieldexists(in_field) == False:
            print(f"{self.basename} {in_field} field does not exist")
        elif int(arcpy.GetCount_management(self.basename).getOutput(0)) > 1 and self.basename != self.config["myFeatureClass"]["basename"]:
            print(f"Processing {self.basename}")
            maxvalue = self.getmaxvalue(in_field)
            edit = arcpy.da.Editor(self.path)
            edit.startEditing(False, True)
            edit.startOperation()
            
            with arcpy.da.UpdateCursor(self.basename, in_field, f"{in_field} IS NULL OR {in_field} = ''") as cursor:
                for row in cursor:
                    maxvalue += 1
                    row[0] = maxvalue                 
                    cursor.updateRow(row)
                    
            edit.stopOperation()
            edit.stopEditing(True)

            print(f"{self.basename} {in_field} field updated")

    def updatefield(self, in_field, value, query=None):
        """
        Update a field with a specific value, optionally filtered by a query.
        """
        if self.validatefieldexists(in_field) == False:
            print(f"{self.basename} {in_field} field does not exist")
        elif int(arcpy.GetCount_management(self.basename).getOutput(0)) > 1:                    
            edit = arcpy.da.Editor(self.path)
            edit.startEditing(False, True)
            edit.startOperation()
            
            with arcpy.da.UpdateCursor(self.basename, in_field, query) as cursor:
                for row in cursor:
                    row[0] = value                 
                    cursor.updateRow(row)
                    
            edit.stopOperation()
            edit.stopEditing(True)

            print(f"{self.basename} {in_field} field updated")

            
    def updatelength(self, in_field, code=None):
        """
        Update a field with length calculations.

        """
        if self.validatefieldexists(in_field[0]) == False:
            print(f"{self.basename} {in_field[0]} field does not exist")
            
        elif int(arcpy.GetCount_management(self.basename).getOutput(0)) > 1:
            arcpy.CalculateField_management(self.basename, in_field[0],  in_field[1], "PYTHON_9.3", code)
            print(f"{self.basename} {in_field[0]} field updated")


    def updatefieldbyjoin(self, join_field1, joinfc, join_field2, calc_field, value, query=None, code=None):
        """
        Update a field based on a join with another feature class or table.
        """
        
        arcpy.env.overwriteOutput = True
        
        if self.validatefieldexists(join_field1) == False:
            print(f"{self.basename} {join_field1} field does not exist")
        elif self.validatefieldexists(calc_field) == False:
            print(f"{self.basename} {calc_field} field does not exist")
                        
        elif int(arcpy.GetCount_management(self.basename).getOutput(0)) > 1:
            arcpy.MakeFeatureLayer_management(self.basename, "basename", "")
            arcpy.AddJoin_management("basename", join_field1, joinfc, join_field2)
            arcpy.SelectLayerByAttribute_management("basename", "NEW_SELECTION", query)
            if int(arcpy.GetCount_management("basename").getOutput(0)) > 1:
                arcpy.CalculateField_management("basename", calc_field,  "!" + value + "!", "PYTHON_9.3", code)
                print(f"{self.basename} {calc_field} field updated")
    def updatefieldbyspatialjoin(self, update_field, join_table, join_key, join_value, query=None):
        """
        Update a field based on spatial join with another table/feature class.

        """         
        arcpy.env.overwriteOutput = True
        
        if self.validatefieldexists(update_field) == False:
            print(f"{self.basename} {update_field} field does not exist")
            
        elif self.validatefieldexists(join_key) == False:
            print(f"{self.basename} {join_key} field does not exist")
            
        elif int(arcpy.GetCount_management(self.basename).getOutput(0)) > 1:
            arcpy.SpatialJoin_analysis(self.basename, join_table, "in_memory\\temp_join", "JOIN_ONE_TO_ONE", "KEEP_COMMON", "", "INTERSECT", "", "")
            
            edit = arcpy.da.Editor(self.path)
            edit.startEditing(False, True)
            edit.startOperation()
            
            # Create Dictionary using modern Python 3 syntax
            with arcpy.da.SearchCursor("in_memory\\temp_join",[join_key, join_value]) as srows:
                path_dict = {srow[0]: srow[1] for srow in srows}
                
            # Update Cursor
            with arcpy.da.UpdateCursor(self.basename,[join_key, update_field], query) as urows:
                for row in urows:
                    if row[0] in path_dict:
                        row[1] = path_dict[row[0]]
                        urows.updateRow(row)
                    
            edit.stopOperation()
            edit.stopEditing(True)
            print(f"{self.basename} {update_field} field updated via spatial join") 
                        
    def updateassetid(self, configtable, in_fieldpk, update_field, in_fields):
        """
        Update asset ID field based on configuration table settings.

        """
        if self.validatefieldexists(update_field) == False:
            print(f"{self.basename} {update_field} field does not exist")

        elif self.validatefieldexists(in_fieldpk) == False:
            print(f"{self.basename} {in_fieldpk} field does not exist")
            
        elif int(arcpy.GetCount_management(self.basename).getOutput(0)) > 1:        
            fName = self.basename.split(".")[2]
            expression = arcpy.AddFieldDelimiters(configtable, "FeatureClass") + " = '" + fName + "'"

            edit = arcpy.da.Editor(self.path)
            edit.startEditing(False, True)
            edit.startOperation()
                    
            with arcpy.da.SearchCursor(configtable, in_fields, where_clause=expression) as cursor:
                for row in cursor:
                    fc = row[0]
                    shp = row[1]
                    query = row[2]
                    prefix = row[3]

                    # Update Cursor with modern Python 3 string formatting
                    with arcpy.da.UpdateCursor(self.basename,[in_fieldpk, update_field], query) as urows:
                        for row in urows:
                            # Create zero-padded asset ID
                            row_id = str(row[0])
                            padding = '000000'[:-len(row_id)] if len(row_id) < 6 else ""
                            row[1] = f"{prefix}{padding}{row_id}"
                            urows.updateRow(row)
                print(f"{self.basename} {update_field} field updated")

            edit.stopOperation()
            edit.stopEditing(True) 

