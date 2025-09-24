import arcpy

class mydatabase:
    def __init__(self, database):
        self.databasepath = database
##        desc = arcpy.Describe(database)
##        cp = desc.connectionProperties
##        
##        self.connectionproperties = desc.connectionProperties
##        self.connectionstring = desc.connectionString
##        self.currentrelease = desc.currentRelease
##        self.domains = desc.domains
##        self.release = desc.release
##        self.workspacefactoryprogid = desc.workspaceFactoryProgID
##        self.workspacetype =  desc.workspaceType
##
##        self.database= cp.database
##        self.instance= cp.instance
##        self.server= cp.server
##        self.version= cp.version

    def databasepath(self, databasepath):
        return databasepath
    
##    def connectionproperties(self, connectionproperties):
##        return connectionproperties
##
##    def connectionstring(self, connectionstring):
##        return connectionstring
##
##    def currentrelease(self, currentrelease):
##        return currentrelease
##
##    def domains(self, domains):
##        return domains
##
##    def release(self, release):
##        return release
##
##    def workspacefactoryprogid(self, workspacefactoryprogid):
##        return workspacefactoryprogid
##
##    def workspacetype(self, workspacetype):
##        return workspacetype
##
##    def server(self, server):
##        return server
##
##    def instance(self, instance):
##        return instance
##
##    def database(self, database):
##        return database
##
##    def version(self, version):
##        return version

##    def sync(self, toDB):
    
    def tunedb(self):
        arcpy.AcceptConnections(self.databasepath, False)
        arcpy.DisconnectUser(self.databasepath, "ALL")
        print ("start compress")
        arcpy.Compress_management(self.databasepath)
        print ("finish compress")
        arcpy.AcceptConnections(self.databasepath, True)
        print ("start indexes")
        arcpy.RebuildIndexes_management(self.databasepath, "SYSTEM", "", "ALL")
        print ("finish compress")
        print ("start analyze")
        arcpy.AnalyzeDatasets_management(self.databasepath, "SYSTEM", "", "ANALYZE_BASE", "ANALYZE_DELTA", "ANALYZE_ARCHIVE")
        print ("finish analyze"
)
