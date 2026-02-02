import os
import cv2
from PIL import Image
import numpy as np
from tqdm import tqdm

from create_cctv_video import VideoCreator

class ProcessTLVideo:
    def __init__(self, mainPath, camList, FPS):
        self.mainPath = mainPath
        self.camList = camList
        self.FPS = FPS
        self.framePathList = []
        self.nextFrameIndex = 0
        self.FRAME_PATH_STR_SZ = 14
        self.FrameDir = "frames"

    def readVid(self, vidPath):
        
        # Initialize the video capture with the video path
        cap = cv2.VideoCapture(vidPath)
        # Check if the video capture opened successfully
        if not cap.isOpened():
            print("Error: Could not open video stream.")
            exit()
        return cap


    def countFrames(self, vid):
        if vid.isOpened():
            return int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
        return -1


    def isImageInDayTime(self, image):
        # convert image to grayscale
        grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Calculate the image brightens
        brightness = np.array(grayImage).mean()

        # select a threshold brightness
        threshold = 230 # Varies from 0 to 255

        # is it day time?
        return brightness > threshold


    def createFramePath(self):
        currentIdxSZ = len(str(self.nextFrameIndex))
        frameName = '0' * (self.FRAME_PATH_STR_SZ - currentIdxSZ) + str(self.nextFrameIndex) + '.jpg'
        framePath = os.path.join(self.camFramePath, frameName)

        self.nextFrameIndex +=1

        return framePath


    def writeFrame(self, frame):
        framePath = self.createFramePath()
        self.framePathList.append(framePath)
        if not os.path.isfile(framePath):
            cv2.imwrite(framePath, frame)


    def processVidFrames(self, cam):
        # Capture a frame every 10 minutes
        camPath = os.path.join(self.mainPath, cam)
        self.framePath = os.path.join(self.mainPath, self.FrameDir)
        self.camFramePath = os.path.join(self.framePath, cam)
        if not os.path.isdir(self.mainPath):
            os.mkdir(self.mainPath)
        if not os.path.isdir(self.framePath):
            os.mkdir(self.framePath)
        if not os.path.isdir(self.camFramePath):
            os.mkdir(self.camFramePath)
        if not os.path.isdir(camPath):
            os.mkdir(camPath)
        
        # inVidPathList = [os.path.join(camPath, vid) for vid in os.listdir(camPath) if vid.endswith(".AVI")]
        inVidPathList = [os.path.join(camPath, vid) for vid in os.listdir(camPath) if vid.endswith(".AVI")]

        print(f"\n###############Camera {camPath.split('/')[-1]}###############")
        for vidPath in inVidPathList:
            inVid = self.readVid(vidPath)
            pBar = tqdm(total=self.countFrames(inVid), desc=f"Video {vidPath}")
            try:
                while True:
                    ret, frame = inVid.read()
                    # Read a frame from the stream
                    if not ret:
                        print("Failed to retrieve frame. Exiting...")
                        break
    
                    if self.isImageInDayTime(frame):
                        self.writeFrame(frame)
                    self.writeFrame(frame)
                    pBar.update(1)

            except KeyboardInterrupt:
                print("Interrupted by user. Exiting...")
            
            pBar.close()
        
    def createProcessedVid(self, cam):
        frameDirPath = os.path.join(self.mainPath, self.FrameDir, cam)
        self.framePathList = [ os.path.join(frameDirPath, frameName) for frameName in os.listdir(frameDirPath)]
        outVidPath = os.path.join(self.mainPath, cam)
        print(f"####### Start Creating Video {cam} ###########")
        videoCreator = VideoCreator(self.mainPath, frameDirPath)
        videoCreator.createVideo(self.framePathList, outVidPath)


    # Collect all cam videos in one filtered video
    def processVid(self, cam):

        # Capture a frame every 10 minutes
        isFirstFrame = True
        height, width = 0, 0
        # Define the codec and create a VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        outVid = None
        camPath = os.path.join(self.mainPath, cam)
        self.camFramePath = os.path.join(self.mainPath, self.FrameDir, cam)

        if not os.path.isdir(self.camFramePath):
            os.mkdir(self.camFramePath)

        
        inVidPathList = [os.path.join(camPath, vid) for vid in os.listdir(camPath) if vid.endswith(".AVI")]
        isFirstFrame = True
        print(f"\n###############Camera {camPath.split('/')[-1]}###############")
        print(f"########{camPath}########")

        for vidPath in inVidPathList:
            inVid = self.readVid(vidPath)
            pBar = tqdm(total=self.countFrames(inVid), desc=f"Video {vidPath}")
            try:
                while True:
                    ret, frame = inVid.read()

                    
                    # Read a frame from the stream
                    if not ret:
                        print("Failed to retrieve frame. Exiting...")
                        break
                    
                    self.writeFrame(frame)
                    if isFirstFrame:
                        height, width, _ = frame.shape
                        outVid = cv2.VideoWriter(f'{camPath}.avi', fourcc, self.FPS, (width, height))
                        isFirstFrame = False

                    if self.isImageInDayTime(frame):
                        # Write the image to the video
                        outVid.write(frame)
                    pBar.update(1)

            except KeyboardInterrupt:
                print("Interrupted by user. Exiting...")

            # Release the video capture object
            inVid.release()
            pBar.close()
        outVid.release()

    def run(self):
        processVideos = input("Do you want to extract frames (YES), no: ")
        createVideos = input("Do you want to create videos (YES), no: ")

        for _, cam in enumerate(self.camList):
            if processVideos.upper() in ["YES", ""]:  
                self.processVidFrames(cam)
            
            if createVideos.upper() in ["YES", ""]:  
                self.createProcessedVid(cam)


if __name__ == "__main__":
    # mainPath = os.path.join('/mnt/c/Users/Ahmed-Abdelhay', 'Videos')
    mainPath = os.path.join('timelapse_cams', 'onprogress')
    # camList = os.listdir(os.path.join(mainPath, 'frames'))
    # print("Frames Directories: ", camList)
    # camList = ['1', '3' ]
    camList = ['3']
    FPS = 30
    processTLVideo = ProcessTLVideo(mainPath, camList, FPS)
    processTLVideo.run()