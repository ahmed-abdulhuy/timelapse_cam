import os
import cv2
from PIL import Image
import numpy as np
from tqdm import tqdm
from datetime import datetime

def readImage(imagePath):
    return cv2.imread(imagePath)


def readImagesDirectory(directory):
    images = [os.path.join(directory, img) for img in os.listdir(directory) if img.endswith(".png") or img.endswith(".jpg")]
    return images


# Create camera directory
def getAllDateDir():
    # List all entries in the directory and filter out folders
    directory = './raw_cctv_data'
    
    return [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]

# get date and time from image name
# 192.168.8.100_CAM 1_main_20240910050150
def getDate(imgPath):
    strParts = imgPath.split('_')
    dateStr = strParts[-1]
    dateReformated = datetime.strptime(dateStr, "%Y%m%d%H%M%S")
    time = [dateReformated.hour, dateReformated.minute, dateReformated.second]
    return time


# # Filter out images
# # out image list should have 10 minuts interva
# def filterImgList (imgList):
#     filteredImgList = []
#     for img in imgList:
        
# def main():
    # camImgs = 