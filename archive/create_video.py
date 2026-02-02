from datetime import datetime
import os
import cv2
from PIL import Image
import numpy as np
from tqdm import tqdm
import re


def readImage(imagePath):
    return cv2.imread(imagePath)

def isImageInDayTime(image):
    # convert iamge to greyscale
    grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


    # Calculate the image brightness
    brightness = np.array(grayImage).mean()

    # selecte a threshold brightness
    threshold = 0 # Varies from 0 to 255

    # is it day time?
    return brightness > threshold

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
    return (imgDate.minute % 10 == 0) and (imgDate.minute != prevImgDate.minute)

# create video from image list
def createVideo(imgPathList, outVidPath, FPS, cam="Cam"):
    if not len(imgPathList):
        return
    firstImage = readImage(imgPathList[0])
    height, width, _ = firstImage.shape
    prevImgDate = getImgDate(imgPathList[0])
    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video = cv2.VideoWriter(f'{outVidPath}.avi', fourcc, FPS, (width, height))
    counter = 0
    
    for idx, imgPath in enumerate(tqdm(imgPathList, desc=f"{cam} video creation progress")):
            try:
                img = readImage(imgPath)
                imgDate = getImgDate(imgPath)
                # if isImgAlignWithInterval(imgDate, prevImgDate) or not idx :
                    # Write the image to the video
                video.write(img)
                counter += 1
                prevImgDate = imgDate
            except:
                print(f'There is some problem with image: {imgPath}')
    # Release the video writer object
    print(f'Number of day picturs is {counter}')
    video.release()


def readImagesDirectory(directory):
    images = [os.path.join(directory, img) for img in os.listdir(directory) if img.endswith(".png") or img.endswith(".jpg")]
    return images


# Create camera directory
def getAllDateDir():
    # List all entries in the directory and filter out folders
    directory = './raw_cctv_data'
    
    return [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]


def getCamALLDateDirList(dateDirList, camPath):
    return [os.path.join(dataDir, camPath) for dataDir in dateDirList]


def main():
    allDateDir = getAllDateDir()
    camList = [ 'Cam 5']#, 'Cam 2', 'Cam 3', 'Cam 4', 'Cam 5', 'Cam 6', 'Cam 7',]
    outDir = './out_video_test'
    FPS = 30
    for cam in camList:
        camDirList = getCamALLDateDirList(allDateDir,  cam)
        camImgArr = np.array([])
        print(camDirList)
        for camDateDire in camDirList:
            camDateImgList = readImagesDirectory(camDateDire)
            # print(camDateImgList[0])
            camImgArr = np.concatenate([camImgArr, camDateImgList])
        
        # Write video
        createVideo(camImgArr, os.path.join(outDir, cam), FPS, cam)



main()