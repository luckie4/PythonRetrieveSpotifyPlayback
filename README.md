# PythonSpotifyAPI
An implementation of the Spotify API using Python.
_This does not utilise the spotipy library, instead it sends HTTP requests to the Spotify API directly._

NEW ADDITION - uSpotify.py --> Spotify integration for Microcontrollers with Web connectivity (e.g. Pi Pico W) running MicroPython.

Object is capable of reading users current queue, adding, and skipping songs in the queue, and reading playlist data.
For more information:
  https://developer.spotify.com/documentation/web-api

For information on how the code is implemented:
  https://developer.spotify.com/documentation/web-api/concepts/authorization



To start you must input the following:
1. Your Client ID
2. Your Client ID and Client Secret, seperated with a : which must be base64 encoded (can be done here --> https://www.base64encode.org/).
3. Your Redirect URI
4. Spotify Scopes

When run for the first time, it will output a url to visit. This url will ask you to sign in and authorize your Spotify Applcation for access to your account. 
It will then redirect you to the set Redirect URI, with a URL query, from which will be ?code= which will need to be copied after the equal sign and pasted into shell.
