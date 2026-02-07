import json
import os
import math
from tqdm import tqdm
from create_cctv_video import VideoCreator
from archive.download_scraper import SnapshotDownloaderScraper
from filter_out_intervals import FilterOutOfIntervalSnapshots
from archive.json_file_processing import SnapshotJsonProcessing
from archive.request_files import SnapshotPathFetcher
from dotenv import load_dotenv

class CCTVVideoCreator:
    def __init__(self, sessionID, startTimeStr, endTimeStr):
        self.HOST_IP = "192.168.1.100" 
        self.DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        self.sessionID = sessionID
        self.startTimeStr = startTimeStr
        self.endTimeStr = endTimeStr
        self.excludedChannels = []
        self.downloadStatus = ['out_of_interval', 'within_interval', 'downloaded', 'download_failed']
        self.downloadMainURL = 'http://admin:Ffi@123321@192.168.1.100/cgi-bin/RPC_Loadfile'
        self.generateFileNames()


    def generateFileNames(self):
        """Generate required file names and directories for the current call"""
        stateName = f"{self.startTimeStr}_{self.endTimeStr}".replace(":", "-")
        # Stat parent Dir
        parentDirName = f"output/{stateName}"
        # fetched NVR image paths Dir
        self.NVRImagePathDir = f"{parentDirName}/NVR_image_path"
        # Create Create processed NVR image paths Filename
        self.processedNVRImagePathFile = f"{parentDirName}/processed_NVR_image_path.json"
        # Create Filter NVR image Paths filename
        self.filteredNVRImagePathFile = f"{parentDirName}/filtered_NVR_image_path.json"
        # Create Images Download Dir
        self.fullPath = os.getcwd()
        self.downloadedImageDir = f"{self.fullPath}/{parentDirName}/downloaded_images"
        # Create Output Videos Dir
        self.outVideoDir = f"{parentDirName}/out_video"
        # Create log file
        self.logDir = f"{parentDirName}/log"


    def fetchImagesNVRPath(self):
        """
            Only Fetch images path in the NVR memory
            Output: Create a directory of json files for collected data Paths in the NVR
        """
        imagesNVTPath = SnapshotPathFetcher(self.sessionID, self.HOST_IP, self.startTimeStr, self.endTimeStr, self.NVRImagePathDir)
        timeIntervalList = imagesNVTPath.getIntervals()
        for interval in timeIntervalList:
            intervalStartTimeStr = interval['startTime']
            intervalEndTimeStr = interval['endTime']
            imagesNVTPath.fetchInterval(intervalStartTimeStr, intervalEndTimeStr)


    def processNVRPath(self):
        """
        Process fetched paths from the NVR to json
        group paths py channel number
        """
        snapshotJsonProcessing = SnapshotJsonProcessing(self.NVRImagePathDir, self.processedNVRImagePathFile)
        channelDict = {idx:[] for idx in range(10)}
        jsonFileList = snapshotJsonProcessing.readJsonDirectory()
        for jsonFilePath in tqdm(jsonFileList, f"Json file: "):
            jsonData = snapshotJsonProcessing.readJson(jsonFilePath)
            for instant in jsonData['infos']:
                if 'Channel' in instant.keys() and instant['Type'] == 'jpg':
                    channelDict[instant['Channel']].append(instant)
        
        # Write out to json file
        with open(snapshotJsonProcessing.outFile, 'w') as json_file:
            json.dump(channelDict, json_file, indent=4)


    def downloadImages(self):
        """
            1- Filter out of interval images.
            2- download image if align with interval.
        """
        filterSnapshots = FilterOutOfIntervalSnapshots(self.processedNVRImagePathFile, self.filteredNVRImagePathFile)
        downloaderScraper = SnapshotDownloaderScraper(self.processedNVRImagePathFile, self.downloadedImageDir, self.downloadMainURL)

        jsonData = filterSnapshots.readJson()
        filteredImgDict = {channel: [] for channel in jsonData.keys()}
        for channel, channelFileList in jsonData.items():
            if(channel in self.excludedChannels or len(channelFileList) == 0):
                continue
            print(channelFileList[0])
            channelFileListSorted = sorted(channelFileList, key=lambda instant:instant['StartTime'], reverse=True)
            lastImgDate = filterSnapshots.getImgDate(channelFileListSorted[0])
            dateSet = set([])
            downloadLog = {}
            downloadFailureCounter = 0
            stepSize = 1
            lastIdx = 0
            for idx, imgObj in enumerate(tqdm(channelFileListSorted, f'Files in channel {channel}')):
                dateSet.add(str(filterSnapshots.getImgDate(imgObj)).split(' ')[0])
                imgDate = filterSnapshots.getImgDate(imgObj)
                appendImageFlag = False
                if idx:
                    if lastIdx + stepSize != idx:
                        # print("stepSize:", stepSize)
                        continue
                    prevImgDate = filterSnapshots.getImgDate(channelFileListSorted[idx-1])
                    if filterSnapshots.isImgAlignWithInterval(imgDate, prevImgDate, 9):
                        appendImageFlag = True

                if filterSnapshots.isImgAlignWithInterval(imgDate, lastImgDate) or (not idx):
                    appendImageFlag = True
                strImgDate = imgDate.strftime('%Y-%m-%d %H:%M:%S')
                downloadLog[strImgDate] = self.downloadStatus[0]
                if appendImageFlag:
                    downloadLog[strImgDate] = self.downloadStatus[1]
                    imageDownloaded = downloaderScraper.downloadImage(imgObj)
                    if imageDownloaded:
                        downloadLog[strImgDate] += f'_{self.downloadStatus[2]}'
                        filteredImgDict[channel].append(imgObj)
                        lastImgDate = imgDate
                        downloadFailureCounter = 0
                        stepSize = 1
                        # print("Rest download failure counter")
                    else:
                        downloadLog[strImgDate] += f'_{self.downloadStatus[3]}'
                        downloadFailureCounter +=stepSize
                        # print("Download failure counter:", downloadFailureCounter)
                        stepSize = min(math.ceil(downloadFailureCounter / 100), 300)
                lastIdx = idx

                # filteredImgDict[channel].append(imgObj)
            print(f"### Collected {len(filteredImgDict[channel])} / {len(channelFileListSorted)}")
            print("Found Dates:", sorted(dateSet))
            if not os.path.isdir(self.logDir):
                os.mkdir(self.logDir)

            with open(f'{self.logDir}/channel_{channel}.json', 'w') as json_file:
                json.dump(downloadLog, json_file, indent=4)
            print('\n')

    
    def createVideos(self):
        videoCreator = VideoCreator(self.outVideoDir, self.downloadedImageDir)
        videoCreator.run()


if __name__ == "__main__":
    load_dotenv()
    sessionID = os.getenv("SESSION_ID")
    startTimeStr = "2024-12-1 00:00:00"
    endTimeStr = "2025-1-1 00:00:00"

    cctvVideoCreator = CCTVVideoCreator(sessionID, startTimeStr, endTimeStr)
    fetchData = input("Do you want to perform file path fetching (YES), no: ")
    downloadImages = input("Do you want to download images (YES), no: ")
    if fetchData.upper() in ["YES", ""]:
        cctvVideoCreator.fetchImagesNVRPath()
        print("\n## Process fetched NVR Paths ##")
        cctvVideoCreator.processNVRPath()
    print("\n\n================ Download Images ================")
    if downloadImages.upper() in ["YES", ""]:
        cctvVideoCreator.downloadImages()
    print("\n================ Create Videos Images ================")
    cctvVideoCreator.createVideos()
