###########################################################
# pix_sort.py
# 
# This program simplifies the colors in an image using a threshold.
# The algorithm finds successive [R G B] modes of the image, then
# turns all pixels within threshold of the mode the same color as the mode.
#
# Zachary Stone, January 2026
###########################################################
import numpy as np
from PIL import Image, ImageFilter
import sys
from pathlib import Path
import text_inputs as TI

# GLOBALS
COLOR_MAP = np.zeros((256,256,256,3), dtype=np.uint8)
REMAINING_TO_COLOR = np.ones((256,256,256),dtype=bool)
RANGE_MASK = np.zeros((256,256,256),dtype=bool)

# Go through global COLOR_MAP, assign all indices within threshold of [R,G,B] to [R,G,B]
def updateColorMap(R,G,B, threshold):
    rMin = (R - threshold) if (R >= threshold) else 0
    rMax = (R + threshold + 1) if (R <= 256 - threshold - 1) else 256 # upper bound is not inclusive
    gMin = (G - threshold) if (G >= threshold) else 0
    gMax = (G + threshold + 1) if (G <= 256 - threshold - 1) else 256
    bMin = (B - threshold) if (B >= threshold) else 0
    bMax = (B + threshold+ 1 ) if (B <= 256 - threshold - 1) else 256
    RANGE_MASK[rMin:rMax,gMin:gMax,bMin:bMax] = True
    # must not have these MODES overwriting each other where their ranges overlap
    combinedMask = RANGE_MASK & REMAINING_TO_COLOR
    COLOR_MAP[combinedMask] = [R,G,B]
    REMAINING_TO_COLOR[combinedMask] = False
    RANGE_MASK[rMin:rMax,gMin:gMax,bMin:bMax] = False

### MAIN ###
# Inputs:
#   inImg - a PILLOW Image object
#   colorThresh - the threshold for evaluating individual RGBs into
#       the most similar MODE RGB
# Outputs:
#    numpy ndarray in mxnx3, where third dimension is [R G B]
def main(inImg, colorThresh,  blur):
    if (blur): inImg = inImg.filter(filter=ImageFilter.BLUR)
    imgArr = np.asarray(inImg).copy()
    imgDims = np.shape(imgArr)
    # reshape the array so each RGB is its own row.
    flatArr = imgArr.reshape(-1,3)

    # Get a list of all unique pixels
    pixUni, pixUniCounts = np.unique(flatArr, axis=0, return_counts=True)
    pixUniDims = np.shape(pixUni)

    # We need to do some very specific sorting.
    # The primary key (most priorty in sort) for us is GREATER COUNTS
    # The secondary key (breaks ties in case of equivalent counts) is DARKER COLOR
    # All numpy sort functions treat lower values with greater priority. This makes
    # our primary key a little complex, since we want GREATER COUNTS to take priority.
    # A simple solution to this is to make all counts negative, so greater magnitudes
    # have lower value, and thus get treated as higher priority.
    # Since pixUni comes to us already sorted DARKEST first, the index of the color
    # in pixUni is our secondary key, where lower value (lower index) means DARKER color.
    
    # SORTING
    # 1. Make pixUniCounts negative
    # 2. lexsort with pixUniCounts as primary, index of pixUni as secondary
    pixUniCounts = 0 - pixUniCounts
    secondaryKey = np.arange(0,pixUniDims[0]) # pixUni already ordered, no need to argsort to create this list
    accessList = np.lexsort((secondaryKey,pixUniCounts))

    numModes = 0
    ### THIS IS THE COLOR_MAP LOOP
    # 1. Look at pixels in pixUni in order specified by accessList
    # 2. For each unique pixel, consult COLOR_MAP to see if it has been mapped to another color
    # 3. If it has not been mapped to another color, treat it as a MODE, and map other colors to it.
    # 4. After looking through all unique pixel colors, your COLOR_MAP will be complete.
    for i in range(0,pixUniDims[0]):
        uniqueColor = pixUni[accessList[i]]
        R = uniqueColor[0]
        G = uniqueColor[1]
        B = uniqueColor[2]
        # Images where 0,0,0 is a MODE are having problems
        if (R == 0 and G == 0 and B == 0): continue
        # If this color has not yet been mapped to another, it's a MODE.
        if ((COLOR_MAP[R,G,B] == [0,0,0]).all()):
            #print(f"[{R},{G},{B}] IS MAPPED TO: {COLOR_MAP[R,G,B]}")
            updateColorMap(R,G,B, colorThresh)                                                            
            print(f"MODE {numModes}: {uniqueColor} - Count {-pixUniCounts[accessList[i]]}")
            numModes += 1 
    ### THIS IS THE COLOR_MAP LOOP

    print(f"{pixUniDims[0]} colors assessed. {numModes} colors kept.")

    ### THIS IS THE IMG MODIFICATION LOOP
    for row in range(0,imgDims[0]):
        for col in range(0,imgDims[1]):
            R = imgArr[row,col,0]
            G = imgArr[row,col,1]
            B = imgArr[row,col,2]
            imgArr[row,col] = COLOR_MAP[R,G,B]
    ### THIS IS THE IMG MODIFICATION LOOP 

    # Return the resulting image array
    return imgArr

# Returns the index in sys.argv[] containing the value for the string desired argument
def getArgIndx(strArg):
    retVal = None
    for i in range(0,len(sys.argv)):
        if (sys.argv[i] == strArg) and (i < len(sys.argv) - 1):
            retVal = i+1
            break
    return retVal

# For execution as main module
if __name__ == "__main__":
    IMAGES_DIR = "./input_images"
    # Get user's arguments or defaults
    FILE_PATH, COLOR_THRESH, BLUR_OPT, LENS_SIZE = TI.getInputArgs()
    # check if user selected a file
    if (FILE_PATH != None):
        FILE_PATH = Path(f"{IMAGES_DIR}/{FILE_PATH}")
    else:
        FILE_PATH = Path(f"{IMAGES_DIR}/burlington-sunset.jpg")

    print("### PIXEL SORTER ###\n" \
        f"Color Threshold: {COLOR_THRESH}\n" \
        f"Blur Option: {BLUR_OPT}\n" \
        f"Selected Image: {FILE_PATH.name}")

    inImg = Image.open(FILE_PATH)
    outArr = main(inImg, COLOR_THRESH, BLUR_OPT)
    inImg.close()
    outImg = Image.fromarray(outArr)
    outImg.show()
