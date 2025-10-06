import sys, string, os, datetime, traceback, arcpy, smtplib, json
from typing import Dict, Any

def loadConfig() -> Dict[str, Any]:
    """
    Load configuration from config.json file.
    
    Returns:
        Dictionary containing myError configuration
        
    Raises:
        RuntimeError: If config file cannot be loaded
    """
    try:
        configPath = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(configPath, 'r') as configFile:
            config = json.load(configFile)
        
        if 'myError' not in config:
            raise RuntimeError("Missing 'myError' section in config.json")
            
        return config['myError']
        
    except FileNotFoundError:
        raise RuntimeError(f"Config file not found: {configPath}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON in config file: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Failed to load configuration: {str(e)}")

class myerror:
    """
    Comprehensive error handling and logging class for ArcGIS Python scripts.
    
    This class provides functionality for:
    - Creating and managing log files
    - Tracking process execution times
    - Capturing and reporting errors
    - Sending email notifications for critical errors
    - Recording variable states for debugging
    
    Attributes:
        logfile: File handle for the log file
        processname: Name of the currently running process
        starttime: Timestamp when the current process started
    """
    
    def __init__(self, logfile):
        """
        Initialize the error handler with a log file path.
        
        Args:
            logfile (str): Path to the log file where messages will be written
        """
        self.logfile = logfile

    def logfile(self, logfile):
        """
        Get the current log file path.
        
        Args:
            logfile (str): Log file path
            
        Returns:
            str: The log file path
        """
        return logfile
    
    def openlog(self):
        """
        Open the log file for writing (append mode).
        Note: This method currently doesn't assign the file handle.
        """
        open(self.logfile,"a")

    def starttime(self):
        """
        Get the start time of the current process.
        
        Returns:
            datetime: The timestamp when the current process started
        """
        return self.starttime if hasattr(self, 'starttime') else None

    def processname(self):
        """
        Get the name of the current process.
        
        Returns:
            str: The name of the currently running process
        """
        return self.processname if hasattr(self, 'processname') else None

    def startlog(self):
        """
        Initialize the log file with header information and timestamp.
        
        Creates a formatted header in the log file with decorative borders
        and records the time when logging was started.
        """
        self.logfile = open(self.logfile,"a")
        self.logfile.write("\n")
        # Write decorative header to separate log sessions
        self.logfile.write("***********----------------------------***********\n")
        self.logfile.write("***********----------------------------***********\n")
        self.logfile.write("\n")
        # Record the start time of this logging session
        self.logfile.write(f"Logfile started at {datetime.datetime.now()}\n")
        
    def startprocess(self, processname):
        """
        Begin tracking a new process with timing and logging.
        
        Args:
            processname (str): Name of the process being started
            
        Records the process name and start time for later duration calculation.
        """
        self.processname = processname
        self.starttime = datetime.datetime.now()
        self.logfile.write("\n")
        # Write section separator for this process
        self.logfile.write("----------------------------\n")
        self.logfile.write("\n")
        # Log process start with timestamp
        self.logfile.write(f"{processname} started at {self.starttime}\n")

    def finishprocess(self):
        """
        Complete the current process and log execution summary.
        
        Calculates and logs the total execution time, then captures
        all local variables for debugging purposes.
        """
        self.logfile.write("\n")
        # Calculate and log total execution time
        execution_time = datetime.datetime.now() - self.starttime
        self.logfile.write(f"{self.processname} completed successfully in {execution_time}\n")
        self.logfile.write("\n")
        
        # Capture all local variables for debugging (helps with troubleshooting)
        local_vars = locals()
        for var_name, var_value in local_vars.items():
            self.logfile.write(f"VARIABLE - {var_name} = {var_value}\n")
        
    def finishlog(self):
        """
        Close the logging session and finalize the log file.
        
        Writes a footer with completion timestamp and closes the file handle.
        """
        self.logfile.write("\n")
        # Write section separator
        self.logfile.write("----------------------------\n")
        # Record when logging session ended
        self.logfile.write(f"Logfile finished at {datetime.datetime.now()}\n")
        # Close the file handle to ensure data is written
        self.logfile.close()

    def getexceptions(self):
        """
        Capture and handle exceptions with comprehensive error reporting.
        
        This method:
        1. Captures Python traceback information
        2. Gets ArcPy specific error messages
        3. Logs all error details to the log file
        4. Captures variable states for debugging
        5. Sends email notification about the error
        
        The method automatically extracts the script name from sys.argv[0]
        and uses configuration settings for email notifications.
        """
        # Capture the traceback object for detailed error information
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]

        # Build comprehensive error message combining Python and ArcPy errors
        pymsg = f"PYTHON ERRORS:\nTraceback info:\n{tbinfo}\nError Info:\n{str(sys.exc_info()[1])}"
        msgs = f"ArcPy ERRORS:\n{arcpy.GetMessages(2)}\n"

        # Add error messages to ArcPy's message system (visible in ArcGIS tools)
        arcpy.AddError(pymsg)
        arcpy.AddError(msgs)

        # Write detailed error information to log file
        self.logfile.write(f"{pymsg}\n")
        self.logfile.write(f"{msgs}")
        
        # Capture all local variables at time of error (crucial for debugging)
        local_vars = locals()
        for var_name, var_value in local_vars.items():
            self.logfile.write(f"VARIABLE - {var_name} = {var_value}\n")
            
        # Send email notification about the error using configuration settings
        # Load configuration for email settings
        config = loadConfig()
        emailTo = config.get('brettEmail', 'brett.angel@spwater.org;')
        mailHost = config.get('email', 'mail.sammplat.wa.org')
        
        # Extract script name from command line arguments for email subject
        script_path_parts = sys.argv[0].split("\\")
        scriptName = f"{script_path_parts[-1][:-3]}.py - ERROR"
        
        error_message = f"{pymsg}\n\n{msgs}"
        self.emailerror(emailTo, "", scriptName, error_message, mailHost)

    def emailerror(self, to, from_, subject, text, host):
        """
        Send error notification email using SMTP.
        
        Args:
            to (str): Recipient email address(es), semicolon-separated
            from_ (str): Sender email address (can be empty)
            subject (str): Email subject line
            text (str): Email body content with error details
            host (str): SMTP server hostname
            
        This method constructs a properly formatted email message
        and sends it via the specified SMTP server. Used for critical
        error notifications to ensure issues are promptly addressed.
        """
        # Construct RFC-compliant email message with proper headers
        body = "\r\n".join((
            f"From: {from_}",
            f"To: {to}",
            f"Subject: {subject}",
            "",  # Empty line separates headers from body
            text  # Error message content
        ))
        
        # Send email via SMTP server
        server = smtplib.SMTP(host)
        server.sendmail(from_, to, body)
        server.quit()
