# This file is to download create a vide out of the downloaded images.
from datetime import datetime
import os
import cv2
from PIL import Image
import numpy as np
from tqdm import tqdm
import re

class VideoCreator:
    def __init__(self, outDir, inputImgDir):
        self.outDir = outDir
        self.inputImgDir = inputImgDir
        if not os.path.exists(self.outDir):
            os.makedirs(self.outDir)


    def readImage(self, imagePath):
        return cv2.imread(imagePath)


    def isImageInDayTime(image):
        # convert image to grayscale
        grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Calculate the image brightens
        brightness = np.array(grayImage).mean()

        # select a threshold brightness
        threshold = 0 # Varies from 0 to 255

        # is it day time?
        return brightness > threshold


    def getImgDate(self, imgName):

        # Get a number starts with '20' and it have 14 digits
        pattern = r'20\d{12}'
        
        # Search for the pattern in the provided text
        match = re.search(pattern, imgName)
        
        # Return the matched number if found, else return None
        dateStr = match.group(0)
        dateReformated = datetime.strptime(dateStr, "%Y%m%d%H%M%S")
        return dateReformated


    # Use it to check if image capturing time is according to interval
    def isImgAlignWithInterval(self, imgDate, prevImgDate):
        return (imgDate.minute % 10 == 0) and (imgDate.minute != prevImgDate.minute)


    # create video from image list
    def createVideo(self, imgPathList, outVidPath, FPS=30, cam="Cam"):
        if not len(imgPathList):
            return
        
        firstImage = None
        firstImageIDX = 0
        while firstImage is None:
            firstImage = self.readImage(imgPathList[firstImageIDX])
            firstImageIDX += 1
        height, width, _ = firstImage.shape
        # prevImgDate = getImgDate(imgPathList[0])
        # Define the codec and create a VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        video = cv2.VideoWriter(f'{outVidPath}.avi', fourcc, FPS, (width, height))
        counter = 0
        
        for idx, imgPath in enumerate(tqdm(imgPathList, desc=f"{cam} video creation progress")):
                try:
                    img = self.readImage(imgPath)
                    # imgDate = getImgDate(imgPath)
                    # if isImgAlignWithInterval(imgDate, prevImgDate) or not idx :
                        # Write the image to the video
                    video.write(img)
                    counter += 1
                    # prevImgDate = imgDate
                except:
                    print(f'There is some problem with image: {imgPath}')
        # Release the video writer object
        print(f'Number of day pictures is {counter}')
        video.release()


    def readImagesDirectory(self, directory):
        images = [os.path.join(directory, img) for img in os.listdir(directory) if img.endswith(".png") or img.endswith(".jpg")]
        return images


    # Create camera directory
    def getImgMainDir(self):
        return [os.path.join(self.inputImgDir, dataDir) for dataDir in os.listdir(self.inputImgDir)]


    def getCamALLDateDirList(self, dateDirList):
        return [dataDir for dataDir in dateDirList]


    def getImgDateFromLocalPath(self, path):
        imgFullName = path.split('/')[-1]
        imgName = imgFullName.split('.')[0]
        imgNameParts = imgName.split(' ')
        return imgNameParts[0]
        


    def createVidPath(self, imagePathList, channelPath):
        channel = channelPath.split('/')[-1]
        if not len(imagePathList):
            return os.path.join(self.outDir, f"Empty_{channel}")
            
        startDate = self.getImgDateFromLocalPath(imagePathList[0])
        endDate = self.getImgDateFromLocalPath(imagePathList[-1])
        videoName = f'{startDate}_{endDate}_({channel})'
        return os.path.join(self.outDir, videoName)

    def run(self):
        allDateDir = self.getImgMainDir()
        FPS = 30
        for channelPath in allDateDir:
            camImgArr = np.array([])
            camImgArr = self.readImagesDirectory(channelPath)
            sortedCamImgArr = sorted(camImgArr)
            # Write video
            videoPath = self.createVidPath(sortedCamImgArr, channelPath)
            self.createVideo(sortedCamImgArr, videoPath, FPS, channelPath)



if __name__ == "__main__":
    outDir = 'out_video_08'
    inputImgDir = 'cctv_images_8'
    createVideo = VideoCreator(outDir, inputImgDir)
    createVideo.run()
