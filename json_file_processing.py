# This file combine all json files in one file
# each property in the object represent a channel
import os
import json
from tqdm import tqdm

class SnapshotJsonProcessing:
    def __init__(self, inputJsonDir, outFile):
        self.inputJsonDir = inputJsonDir
        self.outFile = outFile

    def readJson(self, filePath):
        # Open and read the JSON file
        with open(filePath, 'r') as file:
            data = json.load(file)
        return data


    def readJsonDirectory(self):
        jsonFileList = [os.path.join(self.inputJsonDir, jsonFileName) for jsonFileName in os.listdir(self.inputJsonDir) if jsonFileName.endswith(".json")]
        return jsonFileList


    def run(self):
        channelDict = {idx:[] for idx in range(10)}
        jsonFileList = self.readJsonDirectory()
        for jsonFilePath in tqdm(jsonFileList, f"Json file: "):
            jsonData = self.readJson(jsonFilePath)
            for instant in jsonData['infos']:
                if 'Channel' in instant.keys() and instant['Type'] == 'jpg':
                    channelDict[instant['Channel']].append(instant)
        
        # Write out to json file
        with open(self.outFile, 'w') as json_file:
            json.dump(channelDict, json_file, indent=4)


if __name__ == "__main__":
    inputJsonDir = "cctv_nvr_path_json_08"
    outFile = "organized_img_urls_08.json"
    snapshotJsonProcessing = SnapshotJsonProcessing(inputJsonDir, outFile)
    snapshotJsonProcessing.run()