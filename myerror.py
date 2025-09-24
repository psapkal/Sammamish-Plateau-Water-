import sys, string, os, shutil, datetime, traceback, arcpy, smtplib

class myerror:
    def __init__(self, logfile):     
        self.logfile = logfile

    def logfile(self, logfile):
        return logfile
    
    def openlog(self):
        open(self.logfile,"a")

    def starttime(self):
        return starttime

    def processname(self):
        return processname

    def startlog(self):
        self.logfile = open(self.logfile,"a")
        self.logfile.write("\n")
        self.logfile.write("***********----------------------------***********" + "\n")
        self.logfile.write("***********----------------------------***********" + "\n")
        self.logfile.write("\n")
        self.logfile.write("Logfile started at " + str(datetime.datetime.now()) + "\n")
        
    def startprocess(self, processname):
        self.processname = processname
        self.starttime = datetime.datetime.now()
        self.logfile.write("\n")
        self.logfile.write("----------------------------" + "\n")
        self.logfile.write("\n")
        self.logfile.write(processname + " started at " + str(self.starttime) + "\n")

    def finishprocess(self):
        self.logfile.write("\n")
        self.logfile.write(self.processname + " completed successfully in " + str(datetime.datetime.now() - self.starttime) + "\n")
        self.logfile.write("\n")
        variableCounter = 0                      
        while variableCounter < len(locals()):
            self.logfile.write("VARIABLE - " + str(list(locals())[variableCounter]) + " = " + str(locals()[list(locals())[variableCounter]]) + "\n")
            variableCounter = variableCounter + 1
        
    def finishlog(self):
        self.logfile.write("\n")
        self.logfile.write("----------------------------" + "\n")
        self.logfile.write("Logfile finished at " + str(datetime.datetime.now()) + "\n")
        self.logfile.close()

    def getexceptions(self):
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]

        # Concatenate information together concerning 
        # the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"

        # Return python error messages for use in script tool or Python Window
        arcpy.AddError(pymsg)
        arcpy.AddError(msgs)

        # Print Python error messages for use in Python / Python Window
        self.logfile.write("" + pymsg + "\n")
        self.logfile.write("" + msgs + "")
        variableCounter = 0                      
        while variableCounter < len(locals()):
            self.logfile.write("VARIABLE - " + str(list(locals())[variableCounter]) + " = " + str(locals()[list(locals())[variableCounter]]) + "\n")
            variableCounter = variableCounter + 1
##        self.logfile.close()
##***************************************************************
        self.emailerror("brett.angel@spwater.org;", "", sys.argv[0].split("\\")[len(sys.argv[0].split("\\")) - 1][0:-3] + ".py - ERROR", "" + pymsg + "\n" + "\n" + "" + msgs + "", "mail.sammplat.wa.org")

    def emailerror(self, to, from_, subject, text, host):
        ##HOST = "mail.sammplat.wa.org"
        host = host
        subject = subject
        to = to
        from_ = from_
        text = text
##*************
        body = "\r\n".join((
        "From: %s" % from_,
        "To: %s" % to,
        "Subject: %s" % subject ,
        "",
        text
        ))
        server = smtplib.SMTP(host)
        server.sendmail(from_, to, body)
        server.quit()

##        body = string.join((
##        "From: %s" % from_,
##        "To: %s" % to,
##        "Subject: %s" % subject ,
##        "",
##        text
##        ), "\r\n")
##        server = smtplib.SMTP(host)
##        server.sendmail(from_, to, body)
##        server.quit()
        
