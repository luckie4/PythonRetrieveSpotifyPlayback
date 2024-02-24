import requests
import json    
from datetime import datetime

# Other Programs
from URLEncoding import urlencoding

class Spotify:
    def __init__(self, BASE_64_STRING, CLIENT_ID, REDIRECT_URI, SCOPES, JSON_FILE_FOLDER=""):
        self.BASE_64_STRING = BASE_64_STRING  #Base 64 String of clientid:clientsecret
        self.CLIENT_ID = CLIENT_ID  #Client ID from application on Spotify developer dashboard
        self.REDIRECT_URI = REDIRECT_URI  #Spotify redirect_uri - This must be also defined in the spotify developer console
        self.JSON_FILE_FOLDER = JSON_FILE_FOLDER #Subfolder where JSON files are stored
        self.SCOPES = SCOPES # Scopes required for the spotify request, the ones requried here are - "user-read-playback-state user-read-currently-playing"
        
        self.accessToken = ""
        data = self.__RetrieveCredFile()
        try:
            self.refreshToken = data["REFRESHKEY"]
        except KeyError:
            self.refreshToken = ""
                   
        if self.refreshToken == "":
            print(self.getKeyUrl())
            authKey = input()
            
            self.__GetAuthorizationTokens(authKey)
            data["REFRESHKEY"] = self.refreshToken
            self.__SaveCredFile(data)
        
        else:
            self.__RefreshAccessToken()

    # Returns a URL which the user must go to to get their initial Authorization Token.
    def GetKeyUrl(self):
        return f"https://accounts.spotify.com/authorize?client_id={self.CLIENT_ID}&scope={self.SCOPES}&response_type=code&redirect_uri={self.REDIRECT_URI}" 

    # Turns an Authorization token into a new Auth Token and Refresh Token.
    def __GetAuthorizationTokens(self, token): 
        authHeader = {}
        authHeader["Authorization"] = "Basic " + self.BASE_64_STRING

        url = "https://accounts.spotify.com/api/token"
        form = {
            "code":token,
            "redirect_uri":self.REDIRECT_URI,
            "grant_type":"authorization_code"
        }
        headers = {
            "Authorization":"Basic " + self.BASE_64_STRING,
            "Content-Type":"application/x-www-form-urlencoded"
        }
        form = urlencoding.urlencode(form) # type: ignore

        # Get Spotify Response
        respose = requests.post(url=url, headers=headers, data=form).json()
        
        try:
            self.refreshToken = respose["refresh_token"]
            self.accessToken = respose["access_token"]
            self.accessTokenExpiry = [datetime.now().strftime("%d/%m/%Y %H:%M:%S"),int(respose["expires_in"])]
        except KeyError:
            print(respose)

    # Refreshes an Access token when needed.
    def __RefreshAccessToken(self):
        url = "https://accounts.spotify.com/api/token"
        form = {
            "grant_type": "refresh_token",
            "refresh_token":self.refreshToken
        }
        headers = {
            "Authorization":"Basic " + self.BASE_64_STRING,
            "Content-Type":"application/x-www-form-urlencoded"
        }

        # Get Spotify response
        response = requests.post(url=url, headers=headers, data=urlencoding.urlencode(query=form)).json() # type: ignore
        try:
            self.accessToken = response["access_token"]
            self.accessTokenExpiry = [datetime.now().strftime("%d/%m/%Y %H:%M:%S"),int(response["expires_in"])]
        except KeyError:
            print("InvalidRefreshToken", self.refreshToken)
            return "InvalidRefreshToken"
        try: # Needed because the API does not always respond with a refresh token
            self.refreshToken = response["refresh_token"]
        except KeyError:
            pass

    # Get Playback Data
    def __RequestRawPlayback(self):
        response = requests.get('https://api.spotify.com/v1/me/player',headers={"Authorization": f"Bearer {self.accessToken}"})
        try:
            jsonResponse = response.json()
            return jsonResponse
        except:
            self.__RefreshAccessToken()
            self.__RequestRawPlayback()

    # Return Playback Data in a readable format to user.
    def RequestPlayback(self):
        jsonResponse = self.__RequestRawPlayback()
        
        trackID = jsonResponse['item']['id']
        trackName = jsonResponse['item']['name']
        names = []
        for i in range(0, len(jsonResponse['item']['artists'])):
            names.append(jsonResponse['item']['artists'][i]["name"])
        trackArtists = ", ".join(names)
        link = jsonResponse['item']['external_urls']['spotify']
        lqAlbumArt = jsonResponse["item"]["album"]["images"][2]["url"]
        hqAlbumArt = jsonResponse["item"]["album"]["images"][0]["url"]
        playing = jsonResponse["is_playing"]

        trackData = {
            "id":trackID,
            "name":trackName,
            "artists":trackArtists,
            "link":link,
            "hq_art":hqAlbumArt,
            "art":lqAlbumArt,
            "playing":playing
        }

        return trackData

    # Read Credentials File
    def __RetrieveCredFile(self):
        with open(f"{self.JSON_FILE_FOLDER}credentials.json","r") as f:
            data = json.load(f)
        return data

    # Save Credentials File
    def __SaveCredFile(self, data):
        with open(f"{self.JSON_FILE_FOLDER}credentials.json", "w") as f:
            json.dump(data, f)
