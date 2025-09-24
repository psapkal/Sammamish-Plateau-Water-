# For Http calls
import urllib, json
import http.client
##import httplib

# For system tools
import sys

# For reading passwords without echoing
import getpass

# Defines the entry point into the script
def  startstopservice(folder, startstop):
    # Print some info
    print
    print ("This tool is a sample script that stops or starts all services in a folder.")
    print  

    # Ask for admin/publisher user name and password
    username = "siteadmin"
    password = "siteadmin"
    
    # Ask for server name
    serverName = "geoserver1"
    serverPort = 6080

    folder = folder
    stopOrStart = startstop
    
    # Check to make sure stop/start parameter is a valid value
    if str.upper(stopOrStart) != "START" and str.upper(stopOrStart) != "STOP":
        print ("Invalid STOP/START parameter entered")
        return
    
    # Get a token
    token = getToken(username, password, serverName, serverPort)
    if token == "":
        print ("Could not generate a token with the username and password provided.")
        return
    
    # Construct URL to read folder
    if str.upper(folder) == "ROOT":
        folder = ""
    else:
        folder += "/"
            
    folderURL = "/arcgis/admin/services/" + folder
    
    # This request only needs the token and the response formatting parameter 
    params = urllib.parse.urlencode({'token': token, 'f': 'json'})
    
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    
    # Connect to URL and post parameters    
    httpConn = http.client.HTTPConnection(serverName, serverPort)
    httpConn.request("POST", folderURL, params, headers)
    
    # Read response
    response = httpConn.getresponse()
    if (response.status != 200):
        httpConn.close()
        print ("Could not read folder information.")
        return
    else:
        data = response.read()
        
        # Check that data returned is not an error object
        if not assertJsonSuccess(data):          
            print ("Error when reading folder information. " + str(data))
        else:
            print ("Processed folder information successfully. Now processing services...")

        # Deserialize response into Python object
        dataObj = json.loads(data)
        httpConn.close()

        # Loop through each service in the folder and stop or start it    
        for item in dataObj['services']:

            fullSvcName = item['serviceName'] + "." + item['type']

            # Construct URL to stop or start service, then make the request                
            stopOrStartURL = "/arcgis/admin/services/" + folder + fullSvcName + "/" + stopOrStart
            httpConn.request("POST", stopOrStartURL, params, headers)
            
            # Read stop or start response
            stopStartResponse = httpConn.getresponse()
            if (stopStartResponse.status != 200):
                httpConn.close()
                print ("Error while executing stop or start. Please check the URL and try again.")
                return
            else:
                stopStartData = stopStartResponse.read()
                
                # Check that data returned is not an error object
                if not assertJsonSuccess(stopStartData):
                    if str.upper(stopOrStart) == "START":
                        print ("Error returned when starting service " + fullSvcName + ".")
                    else:
                        print ("Error returned when stopping service " + fullSvcName + ".")

                    print (str(stopStartData))
                    
                else:
                    print ("Service " + fullSvcName + " processed successfully.")

            httpConn.close()           
        
        return


# A function to generate a token given username, password and the adminURL.
def getToken(username, password, serverName, serverPort):
    # Token URL is typically http://server[:port]/arcgis/admin/generateToken
    tokenURL = "/arcgis/admin/generateToken"
    
    params = urllib.parse.urlencode({'username': username, 'password': password, 'client': 'requestip', 'f': 'json'})
    
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    
    # Connect to URL and post parameters
    httpConn = http.client.HTTPConnection(serverName, serverPort)
    httpConn.request("POST", tokenURL, params, headers)
    
    # Read response
    response = httpConn.getresponse()
    if (response.status != 200):
        httpConn.close()
        print ("Error while fetching tokens from admin URL. Please check the URL and try again.")
        return
    else:
        data = response.read()
        httpConn.close()
        
        # Check that data returned is not an error object
        if not assertJsonSuccess(data):            
            return
        
        # Extract the token from it
        token = json.loads(data)        
        return token['token']            
        

# A function that checks that the input JSON object 
#  is not an error object.
def assertJsonSuccess(data):
    obj = json.loads(data)
    if 'status' in obj and obj['status'] == "error":
        print ("Error: JSON object returns an error. " + str(obj))
        return False
    else:
        return True
    
if __name__ == "__main__":
    startstopservice(folder, startstop)
