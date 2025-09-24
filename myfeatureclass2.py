import arcpy

##            with arcpy.da.SearchCursor(self.basename, field, query) as cursor:
##                for row in cursor:
##                    print row

class myfeatureclass:
    def __init__(self, featureclass):     
        desc = arcpy.Describe(featureclass)
        self.basename = desc.basename
        self.path = desc.path
        self.name = desc.name
        self.file = desc.file

    def validatefieldexists(self, in_field):
        in_field = arcpy.ListFields(self.basename, in_field)
        if len(in_field) != 1:
            return False
        else:
            return True
        
    def getmaxvalue(self, in_field):
        values = [row[0] for row in arcpy.da.SearchCursor(self.basename, in_field)]
        uniqueValues = set(values)
        return max(uniqueValues)
    
    def updatenumberincrementbyfield(self, in_field):       
        if self.validatefieldexists(in_field) == False:
            ##print ''.join([self.basename, " ", in_field, " field does not exist."])
            print (self.basename + " field does not exist")
        elif int(arcpy.GetCount_management(self.basename).getOutput(0)) > 1 and self.basename != "production.DBO.ssPump":
            print (self.basename + " does not exist")
            maxvalue = self.getmaxvalue(in_field)
            edit = arcpy.da.Editor(self.path)
            edit.startEditing(False, True)
            edit.startOperation()
            
            with arcpy.da.UpdateCursor(self.basename, in_field, ''.join([in_field, " IS NULL OR ", in_field, " = ''"])) as cursor:
                for row in cursor:
                    maxvalue += 1
                    row[0] = maxvalue                 
                    cursor.updateRow(row)
                    
            edit.stopOperation()
            edit.stopEditing(True)

            ##print ''.join([self.basename, " ", in_field, " field updated."])

    def updatefield(self, in_field, value, query=None):
        if self.validatefieldexists(in_field) == False:
            ##print ''.join([self.basename, " ", in_field, " field does not exist."])
            print ("field does not exist")
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

            ##print ''.join([self.basename, " ", in_field, " field updated."])
            
##    def updatefieldbyjoin(self, join_field1, joinfc, join_field2, calc_field, value, query=None, code=None):
##        
##        arcpy.env.overwriteOutput = True
##        
##        if self.validatefieldexists(join_field1) == False:
##            ##print ''.join([self.basename, " ", join_field1, " field does not exist."])
##            print ("field does not exist")
##        elif self.validatefieldexists(calc_field) == False:
##            ##print ''.join([self.basename, " ", calc_field, " field does not exist."])
##            print ("field does not exist")
##                        
##        elif int(arcpy.GetCount_management(self.basename).getOutput(0)) > 1:
##            arcpy.MakeFeatureLayer_management(self.basename, "basename", "")
##            arcpy.AddJoin_management("basename", join_field1, joinfc, join_field2)
##            ##arcpy.SelectLayerByAttribute_management("basename", "NEW_SELECTION", query)
##            if int(arcpy.GetCount_management("basename").getOutput(0)) > 1:
##                arcpy.CalculateField_management("basename", calc_field,  "!" + value + "!", "PYTHON_9.3", code)
##                print ''.join([self.basename, " ", calc_field, " field updated."])
            
    def updatelength(self, in_field, code=None):
        if self.validatefieldexists(in_field[0]) == False:
            ##print ''.join([self.basename, " ", in_field[0], " field does not exist."])
            print ("field does not exist")
            
        elif int(arcpy.GetCount_management(self.basename).getOutput(0)) > 1:
            arcpy.CalculateField_management(self.basename, in_field[0],  in_field[1], "PYTHON_9.3", code)
            
            ##print ''.join([self.basename, " ", in_field[0], " field updated."])
            print ("field does not exist")

##      ("PROJID", os.path.join(tooldatapath, r"production_test.sde\tbl_projects"), "ProjectNo", "production_test.DBO.PROJNAME", "production_test.DBO.tbl_projects.projname", "PROJNAME IS NULL", "")


    def updatefieldbyjoin(self, join_field1, joinfc, join_field2, calc_field, value, query=None, code=None):
        
        arcpy.env.overwriteOutput = True
        
        if self.validatefieldexists(join_field1) == False:
            ##print ''.join([self.basename, " ", join_field1, " field does not exist 1."])
            print ("field does not exist")
        elif self.validatefieldexists(calc_field) == False:
            ##print ''.join([self.basename, " ", calc_field, " field does not exist 2."])
            print ("field does not exist")
                        
        elif int(arcpy.GetCount_management(self.basename).getOutput(0)) > 1:
            arcpy.MakeFeatureLayer_management(self.basename, "basename", "")
            arcpy.AddJoin_management("basename", join_field1, joinfc, join_field2)
            arcpy.SelectLayerByAttribute_management("basename", "NEW_SELECTION", query)
            if int(arcpy.GetCount_management("basename").getOutput(0)) > 1:
                arcpy.CalculateField_management("basename", calc_field,  "!" + value + "!", "PYTHON_9.3", code)
##                print (''.join([self.basename, " ", calc_field, " field updated."])
                
    def updatefieldbyspatialjoin(self, update_field, join_table, join_key, join_value, query=None):         
        arcpy.env.overwriteOutput = True
        
        if self.validatefieldexists(update_field) == False:
            ##print ''.join([self.basename, " ", update_field, " field does not exist."])
            print ("field does not exist")
            
        elif self.validatefieldexists(join_key) == False:
            ##print ''.join([self.basename, " ", join_key, " field does not exist."])
            print ("field does not exist")
            
        elif int(arcpy.GetCount_management(self.basename).getOutput(0)) > 1:
            arcpy.SpatialJoin_analysis(self.basename, join_table, "in_memory\\temp_join", "JOIN_ONE_TO_ONE", "KEEP_COMMON", "", "INTERSECT", "", "")
            
            edit = arcpy.da.Editor(self.path)
            edit.startEditing(False, True)
            edit.startOperation()
            
            # Create Dictionary
            with arcpy.da.SearchCursor("in_memory\\temp_join",[join_key, join_value]) as srows:
                path_dict = dict([srow[0], srow[1]] for srow in srows)
                
            # Update Cursor
            with arcpy.da.UpdateCursor(self.basename,[join_key, update_field], query) as urows:
                for row in urows:
                    if row[0] in path_dict:
                        row[1] = path_dict[row[0]]
                        urows.updateRow(row)
                    
            edit.stopOperation()
            edit.stopEditing(True) 
                        
    def updateassetid(self, configtable, in_fieldpk, update_field, in_fields):
        if self.validatefieldexists(update_field) == False:
            ##print ''.join([self.basename, " ", update_field, " field does not exist."])
            print ("field does not exist")

        elif self.validatefieldexists(in_fieldpk) == False:
            ##print ''.join([self.basename, " ", in_fieldpk, " field does not exist."])
            print ("field does not exist")
            
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

                    # Update Cursor
                    with arcpy.da.UpdateCursor(self.basename,[in_fieldpk, update_field], query) as urows:
                        for row in urows:
                            row[1] = ''.join([prefix, str('000000'[:-len(str(row[0]))]), str(row[0])])
                            urows.updateRow(row)
                ##print ''.join([self.basename, " ", update_field, " field updated."])
                print ("field does not exist")            

            edit.stopOperation()
            edit.stopEditing(True) 

