import urllib.parse
import json
import http.client
import os
import sys
from typing import Optional, Dict, Any

def loadConfig() -> Dict[str, Any]:
    """
    Load configuration from config.json file.
    
    Returns:
        Dictionary containing myServices configuration
        
    Raises:
        RuntimeError: If config file cannot be loaded
    """
    try:
        configPath = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(configPath, 'r') as configFile:
            config = json.load(configFile)
        
        if 'myServices' not in config:
            raise RuntimeError("Missing 'myServices' section in config.json")
            
        return config['myServices']
        
    except FileNotFoundError:
        raise RuntimeError(f"Config file not found: {configPath}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON in config file: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Failed to load configuration: {str(e)}")

def startStopService(folderName: str, operation: str) -> bool:
    """
    Start or stop all services in a specified folder on ArcGIS Server.
    
    Args:
        folderName: Name of the folder containing services
        operation: "START" or "STOP" operation to perform
        
    Returns:
        True if all operations were successful, False otherwise
    """
    print("ArcGIS Server Service Management Tool")
    print("This tool stops or starts all services in a folder.\n")

    try:
        # Load configuration from config.json
        config = loadConfig()
        
        # Get server credentials from config
        username = config['username']
        password = config['password']
        serverName = config['serverName']
        serverPort = config['serverPort']

        # Validate operation parameter
        if operation.upper() not in ["START", "STOP"]:
            print("Error: Invalid operation parameter. Use 'START' or 'STOP'.")
            return False
        
        operation = operation.upper()
        
        print(f"Operation: {operation} services in folder '{folderName}'")
        print(f"Server: {serverName}:{serverPort}\n")
    
        # Get authentication token
        print("Authenticating with ArcGIS Server...")
        token = getToken(username, password, serverName, serverPort)
        if not token:
            print("Could not generate a token with the provided credentials.")
            return False
            
        print("Authentication successful")
        
        # Construct URL to read folder
        if folderName.upper() == "ROOT":
            folderPath = ""
        else:
            folderPath = f"{folderName}/"
            
        folderURL = f"{config['folderUrl']}{folderPath}"

        # Get list of services in folder
        print(f"Reading services from folder '{folderName}'...")
        
        params = urllib.parse.urlencode({'token': token, 'f': 'json'})
        headers = config['headers']
        
        # Connect to URL and post parameters    
        httpConnection = http.client.HTTPConnection(serverName, serverPort)
        httpConnection.request("POST", folderURL, params, headers)
        
        # Read response
        response = httpConnection.getresponse()
        if response.status != 200:
            httpConnection.close()
            print("Could not read folder information.")
            return False
        else:
            data = response.read()
            
            # Check that data returned is not an error object
            if not assertJsonSuccess(data):          
                print(f"Error when reading folder information: {str(data)}")
                return False
            else:
                print("Folder information retrieved successfully")

            # Deserialize response into Python object
            servicesData = json.loads(data)
            httpConnection.close()

            # Check if there are any services in the folder
            if not servicesData.get('services'):
                print(f"No services found in folder '{folderName}'")
                return True

            print(f"Found {len(servicesData['services'])} service(s) to process...")
            
            # Track operation results
            successCount = 0
            totalCount = len(servicesData['services'])
            
            # Loop through each service in the folder and perform operation    
            for serviceItem in servicesData['services']:
                fullServiceName = f"{serviceItem['serviceName']}.{serviceItem['type']}"
                
                print(f"Processing service: {fullServiceName}")
                
                if processServiceOperation(serverName, serverPort, token, folderPath, 
                                         fullServiceName, operation, config):
                    successCount += 1
            
            # Report results
            print(f"Total services: {totalCount}")
            print(f"Successful: {successCount}")
            print(f"Failed: {totalCount - successCount}")
            
            return successCount == totalCount
        
    except Exception as e:
        print(f"Error in service operation: {str(e)}")
        return False


def processServiceOperation(serverName: str, serverPort: int, token: str, folderPath: str, 
                          serviceName: str, operation: str, config: Dict[str, Any]) -> bool:
    """
    Execute start or stop operation on a specific service.
    
    Args:
        serverName: Server hostname
        serverPort: Server port number
        token: Authentication token
        folderPath: Folder path for the service
        serviceName: Full service name including type
        operation: "START" or "STOP"
        config: Configuration dictionary
        
    Returns:
        True if operation was successful, False otherwise
    """
    try:
        # Construct URL to stop or start service                
        operationURL = f"/arcgis/admin/services/{folderPath}{serviceName}/{operation}"
        
        params = urllib.parse.urlencode({'token': token, 'f': 'json'})
        headers = config['headers']
        
        httpConnection = http.client.HTTPConnection(serverName, serverPort)
        httpConnection.request("POST", operationURL, params, headers)
        
        # Read operation response
        operationResponse = httpConnection.getresponse()
        if operationResponse.status != 200:
            httpConnection.close()
            print(f"Error while executing {operation.lower()} operation. Status: {operationResponse.status}")
            return False
        else:
            operationData = operationResponse.read()
            httpConnection.close()
            
            # Check that data returned is not an error object
            if not assertJsonSuccess(operationData):
                print(f"Error returned when {operation.lower()}ing service {serviceName}.")
                print(str(operationData))
                return False
            else:
                print(f"Service {serviceName} {operation.lower()}ped successfully.")
                return True
                
    except Exception as e:
        print(f"Failed to {operation.lower()} service {serviceName}: {str(e)}")
        return False


def getToken(username: str, password: str, serverName: str, serverPort: int) -> Optional[str]:
    """
    Generate an authentication token for ArcGIS Server admin operations.
    
    Args:
        username: Admin username
        password: Admin password  
        serverName: Server hostname
        serverPort: Server port number
        
    Returns:
        Authentication token string, or None if authentication fails
    """
    try:
        # Load configuration from config.json
        config = loadConfig()

        # Token URL is typically http://server[:port]/arcgis/admin/generateToken
        tokenURL = config['tokenUrl']
        
        params = urllib.parse.urlencode({
            'username': username, 
            'password': password, 
            'client': 'requestip', 
            'f': 'json'
        })

        headers = config['headers']
        
        # Connect to URL and post parameters
        httpConnection = http.client.HTTPConnection(serverName, serverPort)
        httpConnection.request("POST", tokenURL, params, headers)
        
        # Read response
        response = httpConnection.getresponse()
        if response.status != 200:
            httpConnection.close()
            print(f"Error while fetching tokens from admin URL. Status: {response.status}")
            return None
        else:
            data = response.read()
            httpConnection.close()
            
            # Check that data returned is not an error object
            if not assertJsonSuccess(data):            
                return None
            
            # Extract the token from it
            tokenData = json.loads(data)        
            return tokenData['token']
            
    except Exception as e:
        print(f"Failed to get authentication token: {str(e)}")
        return None            
        

def assertJsonSuccess(data: bytes) -> bool:
    """
    Check that the input JSON response is not an error object.
    
    Args:
        data: Raw response data from server
        
    Returns:
        True if response is successful, False if it contains an error
    """
    try:
        responseObj = json.loads(data)
        if 'status' in responseObj and responseObj['status'] == "error":
            print(f"Error: JSON object returns an error. {str(responseObj)}")
            return False
        else:
            return True
    except json.JSONDecodeError:
        print("Error: Invalid JSON response from server")
        return False


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python myservices.py <folder> <START|STOP>")
        print("Example: python myservices.py ROOT START")
        sys.exit(1)
    
    folder = sys.argv[1]
    startstop = sys.argv[2]
    startStopService(folder, startstop)
