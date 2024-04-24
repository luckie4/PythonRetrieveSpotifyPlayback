import urequests as requests

class udatetime:
    def __init__(self, timezone):
        self.url = f"http://worldtimeapi.org/api/timezone/{timezone}"
    
    def now(self) -> str:
        datetime = requests.get(self.url).json()["datetime"]
        return str(datetime[:10]) + " " + str(datetime[11:19])
    
    def getDate(self):
        return requests.get(self.url).json()["datetime"][:10]
    
    def getTime(self):
        return requests.get(self.url).json()["datetime"][11:19]
    
    def getDatetime(self):
        return requests.get(self.url).json()["datetime"]
    
if __name__ == "__main__":
    localtime = udatetime("Europe/London")
    print(localtime.now())
