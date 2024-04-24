import requests
import json    
from datetime import datetime

# Other Programs
from URLEncoding import urlencoding

class Spotify:
    def __init__(self, BASE_64_STRING, CLIENT_ID, REDIRECT_URI, SCOPES, JSON_FILE_FOLDER="") -> None:
        """BASE_64_STRING - Base 64 String of --> clientid:clientsecret\n
        CLIENT_ID - Users client ID from --> https://developer.spotify.com/dashboard\n
        REDIRECT_URI - Found on Spotify Developer Dashboard\n
        SCOPES -> Required scopes for the application to function\n
        JSON_FILE_FOLDER -> Possible subfolder for JSON file"""
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
            
            self.__getAuthorizationTokens(authKey)
            data["REFRESHKEY"] = self.refreshToken
            self.__SaveCredFile(data)
        
        else:
            self.__refreshAccessToken()

    # Returns a URL which the user must go to to get their initial Authorization Token.
    def getKeyUrl(self) -> str:
        """Returns the URL to access the refresh token\n
        Code is stated after ?code="""
        return f"https://accounts.spotify.com/authorize?client_id={self.CLIENT_ID}&scope={self.SCOPES}&response_type=code&redirect_uri={self.REDIRECT_URI}" 

    # Turns an Authorization token into a new Auth Token and Refresh Token.
    def __getAuthorizationTokens(self, token) -> None: 
        """Gets initial refresh and access token, using the intial authorization token."""
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
        response = requests.post(url=url, headers=headers, data=form).json()
        
        try:
            self.refreshToken = response["refresh_token"]
            self.accessToken = response["access_token"]
            self.accessTokenExpiry = [datetime.now().strftime("%d/%m/%Y %H:%M:%S"),int(respose["expires_in"])]
        except KeyError:
            print(response)

    # Refreshes an Access token when needed.
    def __refreshAccessToken(self) -> None:
        """Refreshes the Access token using the Refresh Token when it expires."""
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
            
        try: # Needed because the API does not always respond with a refresh token
            self.refreshToken = response["refresh_token"]
        except KeyError:
            pass

    # Get Playback Data
    def requestPlayback(self) -> json:
        """Returns the users currently playing song as a json object."""
        response = requests.get('https://api.spotify.com/v1/me/player',headers={"Authorization": f"Bearer {self.accessToken}"})
        try:
            if response.status_code == 401:
                self.__refreshAccessToken()
                return self.requestPlayback()
            return response
        except AttributeError as e:
            print(e)
            
            
    # Return Playback Data in a readable format to user.
    def requestFormattedPlayback(self) -> dict:
        """Retrieves the users currently playing song, formats it into the necessary data and outputs it as a dictionary."""
        try:
            jsonResponse = req.json()
        except ValueError:
            return "", req.status_code
        
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

        return trackData, 400

    # Read Credentials File
    def __retrieveCredFile(self) -> dict:
        """Retrieves refresh token from Credentials file."""
        with open(f"{self.JSON_FILE_FOLDER}credentials.json","r") as f:
            data = json.load(f)
        return data

    # Save Credentials File
    def __saveCredFile(self, data) -> None:
        """Saves refresh token to the Credentials file."""
        with open(f"{self.JSON_FILE_FOLDER}credentials.json", "w") as f:
            json.dump(data, f)

        def search(self, query, searchType) -> dict:
        """Searches for a song on the Spoify Database"""
        url = "https://api.spotify.com/v1/search"
        header = {"Authorization": f"Bearer {self.accessToken}"}
        searchQuery = f"?q={query}&type={searchType}"
        return requests.get(f"{url}{searchQuery}", headers=header).json()
    
    def searchAndQueue(self, query) -> json:
        """Searches and Queues a song on the users spotify account."""
        response = self.Search(query, "track")
        newTrack = response["tracks"]["items"][0]["uri"]
        return self.addToQueue(newTrack)
    
    def addToQueue(self, uri) -> json:
        """Adds a track to queue, using the tracks unique identifier."""
        url = "https://api.spotify.com/v1/me/player/queue"
        header = {"Authorization": f"Bearer {self.accessToken}"}
        track = f"?uri={uri}"
        return requests.post(f"{url}{track}", headers=header)
    
    def skip(self, forward) -> json:
        url_fw = "https://api.spotify.com/v1/me/player/next"
        url_bw = "https://api.spotify.com/v1/me/player/previous"
        header = {"Authorization": f"Bearer {self.accessToken}"}
        if forward:
            return requests.post(url_fw, headers=header)
        else:
            return requests.post(url_bw, headers=header)
    
    def getPlaylistItems(self, playlistID) -> dict:
        """Gets the whole contents of a users playlist."""
        url = f"https://api.spotify.com/v1/playlists/{playlistID}/tracks"
        header = {"Authorization": f"Bearer {self.accessToken}"}
        return requests.get(url, headers=header).json()
