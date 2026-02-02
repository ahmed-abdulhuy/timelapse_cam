# This file a scraper to download images 
import time
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from tqdm import tqdm
import glob

class  SnapshotDownloaderScraper:
    def __init__(self, inputFilePath, downloadDir, downloadMainURL):
        self.inputFilePath = inputFilePath
        self.downloadDir = downloadDir
        self.downloadMainURL = downloadMainURL

        if not os.path.isdir(self.downloadDir):
            os.mkdir(self.downloadDir)


    def readFile(self):
        # Open and read the JSON file
        with open(self.inputFilePath, 'r') as file:
            data = json.load(file)
        return data


    def getImgOutDir(self, imageInfo):
        imageOutDir = self.downloadDir + '/' + str(imageInfo['Channel'])
        if not os.path.isdir(imageOutDir):
            os.mkdir(imageOutDir)

        return imageOutDir
    

    # Function to wait until the file is fully downloaded
    def waitForDownloads(self, imgInfo, timeout=3):
        seconds = 0
        imgOutDire = self.getImgOutDir(imgInfo)
        downloadIncomplete = True
        time.sleep(1)
        while downloadIncomplete and seconds < timeout:
            time.sleep(1)  # Wait for 1 second before checking again
            downloadIncomplete = any([filename.endswith(".crdownload") for filename in os.listdir(imgOutDire)])
            seconds += 1
        if seconds >= timeout:
            print("Timeout: Download not completed within the given time.")
            return False
        else:
            pass
            # print(os.listdir(imgOutDire))

        return True


    def createDriver(self, imgInfo):
        # Set Chrome options
        chromeOptions = Options()
        imgOutDir = self.getImgOutDir(imgInfo)
        prefs = {
            "download.default_directory": imgOutDir,  # Change default download directory
            # "download.prompt_for_download": False,  # Disable download prompt
            "directory_upgrade": True  # Ensure downloads go to the new directory
        }
        chromeOptions.add_experimental_option("prefs", prefs)
        chromeOptions.add_argument("--headless")  # Run Chrome in headless mode
        chromeOptions.add_argument("--no-sandbox")  # Recommended for running in headless mode
        chromeOptions.add_argument("--disable-gpu")  # Disable GPU, useful for headless mode
        # Initialize the Chrome WebDriver with options
        service = Service()
        driver = webdriver.Chrome(service=service, options=chromeOptions)
        return driver


    def getImageName(self, imgInfo):
        # Create new file path
        imgOutDire = self.getImgOutDir(imgInfo)
        newFilePath = os.path.join(imgOutDire, f"{imgInfo['StartTime']} {str(imgInfo['Channel'])}.jpg")
        return newFilePath


    def removeInCompleteDownloads(self, imgInfo):
        # Find all files that end with '.crdownload'
        imgOutDire = self.getImgOutDir(imgInfo)
        crdownload_files = glob.glob(os.path.join(imgOutDire, "*.crdownload"))
        
        # Loop through the list and remove each file
        for file in crdownload_files:
            try:
                os.remove(file)
            except FileNotFoundError:
                print(f"File not found: {file}")
            except OSError as e:
                print(f"Error removing file {file}: {e}")
        

    def changeImageName(self, imgInfo):
        # Get file name
        fileName = imgInfo['FilePath'].split('/')[-1]
        # create th full path to the image
        imgOutDire = self.getImgOutDir(imgInfo)
        filePath = os.path.join(imgOutDire, fileName)
        newFilePath = self.getImageName(imgInfo)
        # Create out directory if not exist
        if not os.path.exists(imgOutDire):
            os.mkdir(imgOutDire)
        # Rename file
        if os.path.exists(newFilePath) and os.path.exists(newFilePath):
            os.remove(filePath)
        elif os.path.exists(filePath):
            os.rename(filePath, newFilePath)
        


    def isImgDownloaded(self, imgInfo):
        imgLocalPath = self.getImageName(imgInfo)
        if os.path.exists(imgLocalPath):
            return True
        return False


    def downloadImage(self, imgInfoDict):
        try:
            imgNVRPath = imgInfoDict['FilePath']
            imgURL = self.downloadMainURL + imgNVRPath
            if self.isImgDownloaded(imgInfoDict):
                return True
            
            driver = self.createDriver(imgInfoDict)
            driver.get(imgURL)
            downloadFinished = self.waitForDownloads(imgInfoDict)
            if downloadFinished:
                self.changeImageName(imgInfoDict)
                return True
            
        except Exception as err:
            print(err)
            # print("Image is not downloadable")
            pass
        
        self.removeInCompleteDownloads(imgInfoDict)
        return False


    def run(self):
        jsonDateFile = self.readFile()
        for channel, channelData in jsonDateFile.items():
            print('\n\n######################################')
            print(f"###### Start download channel {channel} ######")
            print('######################################')
            for imgInfo in tqdm(channelData, "Downloaded Images from the JSON file:"):
                self.downloadImage(imgInfo)


if __name__ == "__main__":
    inputFilePath = "filtered_json_data.json"
    currentDir = os.getcwd()
    downloadDir = f"{currentDir}/cctv_images_trial"
    downloadMainURL = 'http://admin:Ffi@123321@192.168.1.100/cgi-bin/RPC_Loadfile'

    snapshotDownloaderScraper = SnapshotDownloaderScraper(inputFilePath, downloadDir, downloadMainURL)
    snapshotDownloaderScraper.run()
