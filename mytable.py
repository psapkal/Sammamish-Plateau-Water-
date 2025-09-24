import arcpy, os

class mytable:
    def __init__(self, table):
        desc = arcpy.Describe(table)
        self.basename = desc.basename
        self.path = desc.path
        self.isversioned = desc.isVersioned
        self.table = os.path.join(self.path, self.basename)
                 
    def basename(self, basename):
        return basename
        
    def path(self, path):
        return path

    def isversioned(self, isversioned):
        return isversioned

    def table(self, table):
        return table
    
    def updatetable(self, sourcetable):
        if self.isversioned:
            arcpy.DeleteRows_management(self.table)
            arcpy.Append_management(sourcetable, self.table, "NO_TEST", "", "")
        else:
            print ("not versioned " + sourcetable)
            arcpy.TruncateTable_management(self.table)
            arcpy.Append_management(sourcetable, self.table, "NO_TEST", "", "")
