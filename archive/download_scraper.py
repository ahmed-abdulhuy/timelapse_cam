import time
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from tqdm import tqdm


def readJsonDirectory(directory):
    images = [os.path.join(directory, img) for img in os.listdir(directory) if img.endswith(".json")]
    return images


def readFile(filePath):
    # Open and read the JSON file
    with open(filePath, 'r') as file:
        data = json.load(file)
    return data


# Function to wait until the file is fully downloaded
def waitForDownloads(downloadDirectory, timeout=60):
    seconds = 0
    downloadIncomplete = True
    while downloadIncomplete and seconds < timeout:
        time.sleep(1)  # Wait for 1 second before checking again
        downloadIncomplete = any([filename.endswith(".crdownload") for filename in os.listdir(downloadDirectory)])
        seconds += 1
    if seconds >= timeout:
        print("Timeout: Download not completed within the given time.")
    # else:
        # print("Download completed!")


def createDriver(downloadDirectory):
        # Set Chrome options
    chromeOptions = Options()
    prefs = {
        "download.default_directory": downloadDirectory,  # Change default download directory
        "download.prompt_for_download": False,  # Disable download prompt
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

def isImgDownloaded(imgNVRPath, imgOutDir):
    imgLocalPath = imgOutDir + '/' + imgNVRPath.split('/')[-1]
    if os.path.exists(imgLocalPath):
        print(f"img Exist: {imgLocalPath}")
        return True
    return False

def main():

    jsonFileDir = "./cctv_nvr_path_json"
    imageOutMainPath = "/mnt/d/FFI_Work/Timelapse_Records/cctv_images_trial"
    urlPath = 'http://admin:Ffi@123321@192.168.8.100/cgi-bin/RPC_Loadfile'

    jsonFilePathList = readJsonDirectory(jsonFileDir)
    noJSONFiles = len(jsonFilePathList)
    for idx, jsonFilePath in enumerate(jsonFilePathList):
        jsonFile = readFile(jsonFilePath)
        print('\n\n#######################################')
        print(f"###Start json file {idx}/{noJSONFiles}###")
        print('#######################################')

        for imgInfo in tqdm(jsonFile['infos'], "Downloaded Images from the JSON file:"):
            imgNVRPath = imgInfo['FilePath']
            imgChannel = imgInfo['Channel']
            imageOutDir = imageOutMainPath + '/' + str(imgChannel)
            
            if isImgDownloaded(imgNVRPath, imageOutDir):
                continue

            driver = createDriver(imageOutDir)
            imgURL = urlPath + imgNVRPath
            driver.get(imgURL)
            waitForDownloads(imageOutDir)
        
        

main()