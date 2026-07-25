###########################################################
# text_inputs.py
# 
# This code in this file is just meant to help parse inputs
# to the other tools.
#
# Zachary Stone, March 2026
###########################################################
import sys
from pathlib import Path

# Get all images in the given directory
def getImagesInDir(directory_path):
    IMAGE_TYPES = ['.png','.jpg','.jpeg','.bmp']
    p = Path(directory_path)
    # must x.is_file() to ignore subdirectories
    files = [x for x in p.iterdir() if x.is_file()]
    imgs = []
    for file in files:
        if (file.suffix in IMAGE_TYPES):
            imgs.append(file)
    return imgs

# Returns the index in sys.argv[] containing the value for the string desired argument
def getArgIndx(strArg):
    retVal = None
    for i in range(0,len(sys.argv)):
        if (sys.argv[i] == strArg) and (i < len(sys.argv) - 1):
            retVal = i+1
            break
    return retVal

# Process all the user input arguments and provide defaults if none specified
def getInputArgs():
    # check for an input file
    try:
        indx = getArgIndx("-f")
        if (indx != None): FILE_NAME = sys.argv[indx]
        else: FILE_NAME = None
    except: 
        FILE_NAME = None

    # input threshold
    try: 
        indx = getArgIndx("-t")
        if (indx != None): COLOR_THRESH = int(sys.argv[indx])
        else: COLOR_THRESH = 30
    except: 
        COLOR_THRESH = 30

    # input blur
    try:
        indx = getArgIndx("-b")
        if (indx != None and sys.argv[indx].lower() == "true"): BLUR_OPT = True
        else: BLUR_OPT = False
    except: 
        BLUR_OPT = False

    # lens size
    try:
        indx = getArgIndx("-l")
        if (indx != None): LENS_SIZE = int(sys.argv[indx])
        else: LENS_SIZE = 4
    except: 
        LENS_SIZE = 4

    # coloring book generator
    try:
        indx = getArgIndx("-c")
        if (indx != None): COLORING_BOOK = True
        else: COLORING_BOOK = False
    except:
        COLORING_BOOK = False

    return FILE_NAME, COLOR_THRESH, BLUR_OPT, LENS_SIZE, COLORING_BOOK