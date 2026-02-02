# This file request images paths from NVR
import requests
import json
from datetime import datetime, timedelta
import os

class SnapshotPathFetcher:
    def __init__(self, sessionID, hostIP, startTime, endTime, jsonOutDir='cctv_nvr_path_json_02'):
        self.sessionID = sessionID
        self.domain = f"http://{hostIP}"
        self.baseURL = f"{self.domain}/RPC2"
        self.startTime = startTime
        self.endTime = endTime
        self.jsonOutDir = jsonOutDir
        self.headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        # "Content-Length": "122",
        "Content-Type": "application/json",
        "Cookie": f"WebClientHttpSessionID={sessionID}",
        "Host": hostIP,
        "Origin": self.domain,
        "Referer": self.domain,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        }

        if not os.path.exists(self.jsonOutDir):
            os.makedirs(self.jsonOutDir)

    def makeRequest(self, payload):
        """
        This function makes a post request to get json file of snapshots path objects.

        output: request response.
        """
        return requests.post(self.baseURL, json=payload, headers=self.headers)


    def getIntervals(self, interval=10):
        """
        Return a list of time slots between to dates with specific interval length.    
        """
        datetimeFormate = '%Y-%m-%d %H:%M:%S'
        startTime = datetime.strptime(self.startTime, datetimeFormate)
        endTime = datetime.strptime(self.endTime, datetimeFormate)
        datetimeList = []

        while startTime < endTime:
            if startTime.hour < 5 or startTime.hour > 20:
                startTime = startTime + timedelta(minutes=interval)
                continue
            
            intervalDatetime = startTime + timedelta(minutes=interval)
            datetimeList.append({
                'startTime': startTime.strftime(datetimeFormate),
                'endTime': intervalDatetime.strftime(datetimeFormate)
                })
            startTime = startTime + timedelta(minutes=interval)
        
        return datetimeList


    def requestSeq(self, intervalStartTime, intervalEndTime):
        """
        Request snapshots
        """
        clusterRequestPayload = {
                "method":"mediaFileFind.factory.create",
                "params":"null",
                "id":357,
                "session":self.sessionID
            }

        response = self.makeRequest(clusterRequestPayload)
        if(response.status_code != 200):
            print(response.status_code, response.text)
            return
        
        response = response.json()
        cluster = response['result']
        id = int(response['id'])
    
        timeRequestPayload = {
            "method":"mediaFileFind.findFile",
            "params":{
                "condition":{
                    "StartTime":intervalStartTime,
                    "EndTime":intervalEndTime,
                    "Types":["jpg"],
                    "VideoStream":"Main",
                    "Channel":-1
                    }
                },
                "id":id+1,
                "session":self.sessionID,
                "object":cluster
            }

        response = self.makeRequest(timeRequestPayload)
        if(response.status_code != 200):
            print(response.status_code, response.text)
            return
        response = response.json()

        requestFilePath = {
            "method":"mediaFileFind.findNextFile",
            "params":{"count":102400},
            "id":id+1,
            "session":self.sessionID,
            "object":cluster
            }

        filePathListResponse = self.makeRequest(requestFilePath)
        if(filePathListResponse.status_code != 200):
            print(filePathListResponse.status_code, filePathListResponse.text)
            return

        requestFilePath = {
            "method":"mediaFileFind.close",
            "params":'null',
            "id":id+1,
            "session":self.sessionID,
            "object":cluster
            }

        response = self.makeRequest(requestFilePath)
        if filePathListResponse.status_code == 200 and filePathListResponse.json()['params']['found'] > 0:
            return filePathListResponse.json()
        
        return False


    def isFileExist(self, filename):
        """
        Check if file exists
        """
        filePath = f'{self.jsonOutDir}/{filename}.json'
        return os.path.exists(filePath)


    def writeJsonFile(self, filename, data):
        filePath = f'{self.jsonOutDir}/{filename}.json'
        with open(filePath, 'w') as jsonFile:
            json.dump(data, jsonFile, indent=4)
            print(f"File {filename} written successfully")


    def fetchInterval(self, intervalStartTime, intervalEndTime):
        fileName = f'{intervalStartTime}-{intervalEndTime}'
        
        if self.isFileExist(fileName):
            print(f"FILE EXISTS: {fileName}")
            return

        filePathObj = self.requestSeq(intervalStartTime, intervalEndTime)
        if not filePathObj:
            print("ERROR:No data fetched!!!")
            return 
        
        files = filePathObj['params']
        self.writeJsonFile(fileName, files)


    def run(self):
        """
        Main function to run the snapshot fetching process.
        """
        timeIntervalList = self.getIntervals()
        for interval in timeIntervalList:
            intervalStartTime = interval['startTime']
            intervalEndTime = interval['endTime']
            self.fetchInterval(intervalStartTime, intervalEndTime)



if __name__ == "__main__":
    sessionID = '800277e210aaae12cf7f03027fd48efe'
    startTime = "2024-10-13 00:00:00"
    endTime = "2024-10-31 01:00:00"
    hostIP = "192.168.1.100"

    jsonOutDir = "cctv_nvr_path_json_08"

    datetimeFormate = "%Y-%m-%d %H:%M:%S"
    inputStartDate = input(f"Enter Start date in formate ({datetimeFormate}): ")
    inputEndDate = input(f"Enter End date in formate ({datetimeFormate}): ")
    inputSessionID = input("Enter Session ID:")
    if inputSessionID:
        sessionID = inputSessionID
    if inputStartDate:
        startTime = inputStartDate
    if inputEndDate:
        endTime = inputEndDate
    
    snapshotPathFetcher = SnapshotPathFetcher(sessionID, hostIP ,startTime, endTime, jsonOutDir)

    snapshotPathFetcher.run()