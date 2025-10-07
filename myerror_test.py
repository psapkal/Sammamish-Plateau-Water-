import sys
import os
import shutil
import datetime
import traceback
import arcpy
import smtplib
import json
from typing import Optional, Dict, Any

class MyError:
    """
    Error handling and logging utility for ArcGIS Python scripts
    
    Provides methods for:
    - Process logging with timestamps
    - Exception handling and reporting
    - Variable state capture
    - Email error notifications
    """
    
    def __init__(self, logfile: str) -> None:
        """
        Initialize MyError with log file path
        
        Args:
            logfile: Path to the log file
        """
        self.logfile_path = logfile
        self.logfile = None
        self.processname = ""
        self.starttime = None
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from config.json file
        
        Returns:
            Configuration dictionary, or default values if config not found
        """
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
            with open(config_path, 'r', encoding='utf-8') as config_file:
                config = json.load(config_file)
                return config.get('myError', {})
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            # Return default values if config file not found or invalid
            return {
                'brettEmail': 'brett.angel@spwater.org',
                'email': 'mail.sammplat.wa.org'
            }

    def openlog(self) -> None:
        """
        Open the log file for writing
        """
        self.logfile = open(self.logfile_path, "a", encoding='utf-8')

    def startlog(self) -> None:
        """
        Start logging session with timestamp and header
        """
        self.logfile = open(self.logfile_path, "a", encoding='utf-8')
        self.logfile.write("\n")
        self.logfile.write("***********----------------------------***********\n")
        self.logfile.write("***********----------------------------***********\n")
        self.logfile.write("\n")
        self.logfile.write(f"Logfile started at {datetime.datetime.now()}\n")
        
    def startprocess(self, processname: str) -> None:
        """
        Start a new process and log its beginning
        
        Args:
            processname: Name of the process being started
        """
        self.processname = processname
        self.starttime = datetime.datetime.now()
        self.logfile.write("\n")
        self.logfile.write("----------------------------\n")
        self.logfile.write("\n")
        self.logfile.write(f"{processname} started at {self.starttime}\n")

    def finishprocess(self) -> None:
        """
        Log successful completion of process with duration and variable state
        """
        self.logfile.write("\n")
        self.logfile.write(f"{self.processname} completed successfully in {str(datetime.datetime.now() - self.starttime)}\n")
        self.logfile.write("\n")
        variableCounter = 0                      
        while variableCounter < len(locals()):
            self.logfile.write(f"VARIABLE - {str(list(locals())[variableCounter])} = {str(locals()[list(locals())[variableCounter]])}\n")
            variableCounter = variableCounter + 1
        
    def finishlog(self) -> None:
        """
        Close logging session with timestamp
        """
        self.logfile.write("\n")
        self.logfile.write("----------------------------\n")
        self.logfile.write(f"Logfile finished at {datetime.datetime.now()}\n")
        self.logfile.close()

    def getexceptions(self) -> None:
        """
        Handle exceptions with comprehensive logging and email notification
        """
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]

        # Concatenate information together concerning the error into a message string
        pymsg = f"PYTHON ERRORS:\nTraceback info:\n{tbinfo}\nError Info:\n{sys.exc_info()[1]}"
        msgs = f"ArcPy ERRORS:\n{arcpy.GetMessages(2)}\n"

        # Return python error messages for use in script tool or Python Window
        arcpy.AddError(pymsg)
        arcpy.AddError(msgs)

        # Print Python error messages for use in Python / Python Window
        self.logfile.write(f"{pymsg}\n")
        self.logfile.write(f"{msgs}")
        variableCounter = 0                      
        while variableCounter < len(locals()):
            self.logfile.write(f"VARIABLE - {str(list(locals())[variableCounter])} = {str(locals()[list(locals())[variableCounter]])}\n")
            variableCounter = variableCounter + 1
        
        # Send error notification email using config values
        script_name = os.path.basename(sys.argv[0]).replace('.py', '')
        self.emailerror(
            self.config.get('brettEmail', 'brett.angel@spwater.org'), 
            "", 
            f"{script_name}.py - ERROR", 
            f"{pymsg}\n\n{msgs}", 
            self.config.get('email', 'mail.sammplat.wa.org')
        )

    def emailerror(self, to: str, from_: str, subject: str, text: str, host: str) -> None:
        """
        Send error notification email
        
        Args:
            to: Recipient email address
            from_: Sender email address
            subject: Email subject
            text: Email body text
            host: SMTP host server
        """
        try:
            body = "\r\n".join([
                f"From: {from_}",
                f"To: {to}",
                f"Subject: {subject}",
                "",
                text
            ])
            
            server = smtplib.SMTP(host)
            server.sendmail(from_, to, body)
            server.quit()
            
        except Exception as e:
            print(f"Failed to send email notification: {e}")
