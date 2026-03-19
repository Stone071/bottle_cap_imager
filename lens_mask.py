###########################################################
# lens_mask.py
# 
# This program simplifies the colors in an image using a threshold.
# The algorithm finds successive [R G B] modes of the image, then
# turns all pixels within threshold of the mode the same color as the mode.
#
# Zachary Stone, January 2026
###########################################################

# NOTE: THIS IS STILL NOT THE END GOAL. I want the bottle caps to fill
# the color blobs, not be on an even grid.

import numpy as np
from PIL import Image
import math
import pixel_basics as PB
import text_inputs as TI
from pathlib import Path

# GLOBALS
RGB_WHITE = (255,255,255)
RGB_BLACK = (0,0,0)

# Determine if a given pixel specified by coordinates [m,n] is within the bottle
# of size circRad centered at [centerRow, centerCol]
def inLens(m,n,circRad,centerRow,centerCol):
    if (((PB.ezDiff(m,centerRow))**2+(PB.ezDiff(n,centerCol))**2) <= circRad**2):
        return True
    else:
        return False

# Determine the number of lenses spanning the width and length of the image
def getNumLenses(imgArray, circRad):
    dims = np.shape(imgArray)
    circDiameter = circRad * 2
    # Calc number of lenses
    rowLenses = math.ceil(dims[0] / circDiameter)
    colLenses = math.ceil(dims[1] / circDiameter)
    # Let's start with bucketsize for area of circle
    return (rowLenses, colLenses)


# Check the image dimensions so no out of bounds writes
def checkEndpoints(imgDims, brPix):
    rowLim = imgDims[0]
    colLim = imgDims[1]
    if (brPix[0] < rowLim): 
        lensRowEnd = brPix[0]
    else: 
        lensRowEnd = rowLim

    if (brPix[1] < colLim):
        lensColEnd = brPix[1]
    else:
        lensColEnd = colLim
    return (lensRowEnd,lensColEnd)


### MAIN ###
# Inputs:
#   inImg - a PILLOW Image object
#   circleRad - the radius for the lenses to apply
# Outputs:
#    numpy ndarray in mxnx3, where third dimension is [R G B]
def main(inImg, circleRad):
    # Get a 2D array of the pixel (r,g,b) tuples
    imArray = np.asarray(inImg).copy() # copy so not readonly
    imgDims = np.shape(imArray)

    # Create a numpy array which can be used as buckets to hold all
    # the pixel colors contained in each lens.
    rowBuckets, colBuckets = getNumLenses(imArray, circleRad)

    # I think what we need to do is to separate the image into lens sections at the get go, then get the MODE
    # for each section, then look through the pixels in each section and recolor.
    for rowLens in range(0,rowBuckets):
        for colLens in range(0,colBuckets):
            # 1. Make a sub-array of the pixels in the lensed area
            # pixels will be specified in (row,col) form
            tlPix = (rowLens*circleRad*2, colLens*circleRad*2)
            # this form specifies the bottom right pixel as the bottom right 
            # pixel which is just outside the current lens. I think this is fine, 
            # since we will be using this in range(), where the upper limit is 
            # not included in the range.
            brPix = ((rowLens+1)*circleRad*2,(colLens+1)*circleRad*2)
            #print(f"tlPix {tlPix}, brPix {brPix}")
            imArrSection = imArray[tlPix[0]:brPix[0], tlPix[1]:brPix[1]]

            # 2. Flatten it
            flatSection = imArrSection.reshape(-1,3)

            # 3. Get the mode
            sectionMode = PB.getMode(flatSection)
            #print(f"SECTION: {rowLens,colLens}, MODE: {sectionMode[0]}")

            # 4. Recolor the pixels. pixels outside the lens are black, pixels 
            #    inside the lens are MODE
            centerRow = tlPix[0]+circleRad
            centerCol = tlPix[1]+circleRad
            # ensure no out of bounds writes
            lensRowEnd,lensColEnd = checkEndpoints(imgDims,brPix)
            for i in range(tlPix[0],lensRowEnd):
                for j in range(tlPix[1],lensColEnd):
                    if(inLens(i,j,circleRad,centerRow,centerCol)):
                        imArray[i,j] = sectionMode[0]
                    else:
                        imArray[i,j] = RGB_BLACK

    return imArray

# For execution as main module
if __name__ == "__main__":
    IMAGES_DIR = "./input_images"
    # Get user's arguments or defaults
    FILE_PATH, COLOR_THRESH, BLUR_OPT, LENS_SIZE = TI.getInputArgs()
    if (FILE_PATH != None):
        FILE_PATH = Path(f"{IMAGES_DIR}/{FILE_PATH}")
    else:
        FILE_PATH = Path(f"{IMAGES_DIR}/burlington-sunset.jpg")
    
    print("### LENS MASK ###\n" \
        f"Lens Size: {LENS_SIZE}\n" \
        f"Selected Image: {FILE_PATH.name}")
    
    inImg = Image.open(FILE_PATH)
    outArr = main(inImg, LENS_SIZE)
    inImg.close()
    outImg = Image.fromarray(outArr)
    outImg.show()