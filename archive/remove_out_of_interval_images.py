import re
from datetime import datetime
import os
import numpy as np


def readImagesDirectory(directory):
    images = [os.path.join(directory, img) for img in os.listdir(directory) if img.endswith(".png") or img.endswith(".jpg")]
    return images


# Create camera directory
def getAllDateDir():
    # List all entries in the directory and filter out folders
    directory = './raw_cctv_data'
    
    return [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]


def getImgDate(imgName):

    # Get a number satrts with '20' and it have 14 digits
    pattern = r'20\d{12}'
    
    # Search for the pattern in the provided text
    match = re.search(pattern, imgName)
    
    # Return the matched number if found, else return None
    dateStr = match.group(0)
    dateReformated = datetime.strptime(dateStr, "%Y%m%d%H%M%S")
    return dateReformated


# Use it to check if image captiring time is according to interval
def isImgAlignWithInterval(imgDate, prevImgDate):
    return np.abs(imgDate.minute - prevImgDate.minute) >= 10 

# Create camera directory
def getAllDateDir():
    # List all entries in the directory and filter out folders
    directory = './raw_cctv_data'
    
    return [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]


def getCamALLDateDirList(dateDirList, camPath):
    return [os.path.join(dataDir, camPath) for dataDir in dateDirList]


def main():
    allDateDir = getAllDateDir()
    camList = ['Cam 1', 'Cam 2', 'Cam 3', 'Cam 4', 'Cam 5', 'Cam 6', 'Cam 7',]

    for cam in camList:
        camDirList = getCamALLDateDirList(allDateDir,  cam)
        camImgArr = np.array([])
        for camDateDire in camDirList:
            camDateImgList = readImagesDirectory(camDateDire)
            if not len(camDateImgList):
                continue

            prevImgDate = getImgDate(camDateImgList[0])
            for idx, img in enumerate(camDateImgList):
                imgDate = getImgDate(img)
                if isImgAlignWithInterval(imgDate, prevImgDate) or not idx:
                    camImgArr = np.append(camImgArr, img)
                    prevImgDate = getImgDate(img)
                
                else:
                    os.remove(img)
        print(cam, camImgArr.shape)


main()