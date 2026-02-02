# This file create a json file of images
# that follows the interval rule of 10 minutes.
from datetime import datetime
import os
import numpy as np
from tqdm import tqdm
import json 

class FilterOutOfIntervalSnapshots:
    def __init__(self, inputFilePath, outFilePath):
        self.inputFilePath = inputFilePath
        self.outFilePath = outFilePath
    
    
    def readJson(self):
        # Open and read the JSON file
        with open(self.inputFilePath, 'r') as file:
            data = json.load(file)
        return data


    def getImgDate(self, imgObj):
        return datetime.strptime(imgObj['StartTime'], "%Y-%m-%d %H:%M:%S")


    # Use it to check if image capturing time is according to interval
    def isImgAlignWithInterval(self, imgDate, prevImgDate, interval=10):
        return np.abs(imgDate.minute - prevImgDate.minute) >= interval 


    def getCamALLDateDirList(self, dateDirList, camPath):
        return [os.path.join(dataDir, camPath) for dataDir in dateDirList]


    def run(self):
        # Read image URL JSON file
        jsonData = self.readJson()
        filteredImgDict = {channel: [] for channel in jsonData.keys()}
        for channel, channelFileList in jsonData.items():
            # if channel != '9':
            #     continue
            channelFileListSorted = sorted(channelFileList, key=lambda instant:instant['StartTime'])
            lastImgDate = self.getImgDate(channelFileListSorted[0])
            dateSet = set([])
            for idx, imgObj in enumerate(tqdm(channelFileListSorted, f'Files in chanel {channel}')):
                dateSet.add(str(self.getImgDate(imgObj)).split(' ')[0])
                imgDate = self.getImgDate(imgObj)
                appendImageFlag = False
                if idx:
                    prevImgDate = self.getImgDate(channelFileListSorted[idx-1])
                    if self.isImgAlignWithInterval(imgDate, prevImgDate, 9):
                        appendImageFlag = True

                if self.isImgAlignWithInterval(imgDate, lastImgDate) or (not idx):
                    appendImageFlag = True
                    lastImgDate = imgDate

                if appendImageFlag:
                    filteredImgDict[channel].append(imgObj)

                # filteredImgDict[channel].append(imgObj)
            print(f"### Collected {len(filteredImgDict[channel])} / {len(channelFileListSorted)}")
            print("Found Dates:", sorted(dateSet))
            print('\n')

        # Create file
        # Write out to json file
        with open(self.outFilePath, 'w') as json_file:
            json.dump(filteredImgDict, json_file, indent=4)


    
if __name__ == "__main__":
    inputFilePath = 'organized_img_urls_02.json'
    outFilePath = "filtered_json_data.json"
    filterOutOfIntervalSnapshots = FilterOutOfIntervalSnapshots(inputFilePath, outFilePath)
    filterOutOfIntervalSnapshots.run()