import requests
import json    
from datetime import datetime

# Other Programs
from URLEncoding import urlencoding

class Spotify:
    def __init__(self, BASE_64_STRING, CLIENT_ID, REDIRECT_URI, SCOPES, JSON_FILE_FOLDER=""):
        self.BASE_64_STRING = BASE_64_STRING
        self.CLIENT_ID = CLIENT_ID
        self.REDIRECT_URI = REDIRECT_URI
        self.JSON_FILE_FOLDER = JSON_FILE_FOLDER
        self.SCOPES = SCOPES
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

    def GetKeyUrl(self):
        return f"https://accounts.spotify.com/authorize?client_id={self.CLIENT_ID}&scope={self.SCOPES}&response_type=code&redirect_uri={self.REDIRECT_URI}"

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
    
    def __RequestRawPlayback(self):
        return requests.get('https://api.spotify.com/v1/me/player',headers={"Authorization": f"Bearer {self.accessToken}"})

    def __RetrieveCredFile(self):
        with open(f"{self.JSON_FILE_FOLDER}credentials.json","r") as f:
            data = json.load(f)
        return data
    
    def __SaveCredFile(self, data):
        with open(f"{self.JSON_FILE_FOLDER}credentials.json", "w") as f:
            json.dump(data, f)

    def RequestPlayback(self):
        req = self.__RequestRawPlayback()
        try:
            if req.status_code == 401:
                print("Token expired")
                return False
        except AttributeError:
            pass

        try:
            resp_json = req.json()
        except ValueError:
            print(f"Value Error.\n Request Response: {req}")
            
        trackID = resp_json['item']['id']
        trackName = resp_json['item']['name']
        names = []
        for i in range(0, len(resp_json['item']['artists'])):
            names.append(resp_json['item']['artists'][i]["name"])
        trackArtists = ", ".join(names)
        link = resp_json['item']['external_urls']['spotify']
        lqAlbumArt = resp_json["item"]["album"]["images"][2]["url"]
        hqAlbumArt = resp_json["item"]["album"]["images"][0]["url"]
        playing = resp_json["is_playing"]

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
