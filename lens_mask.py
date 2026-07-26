###########################################################
# lens_mask.py
# 
# This program takes an image and sections it into a grid of
# circular lenses, then finds the most common pixel in each
# lens and makes every pixel in the lens that color.
#
# Zachary Stone, January 2026
###########################################################

# NOTE: THIS IS STILL NOT THE END GOAL. I want the bottle caps to fill
# the color blobs, not be on an even grid.

### IMPORTS
import numpy as np
from PIL import Image, ImageOps, ImageDraw
import math
import pixel_basics as PB
import text_inputs as TI
from lens_class import Lens
from pathlib import Path
from tqdm import trange, tqdm

### GLOBALS
RGB_WHITE = (255,255,255)
RGB_BLACK = (0,0,0)
KEY_WIDTH_TO_IMAGE_WIDTH = (2/3)
KEY_TEXT_COLOR = RGB_WHITE
IMG_TEXT_COLOR = RGB_BLACK

### HELPER FUNCS
# Determine the number of lenses spanning the width and length of the image
def getNumLenses(imgArray, circRad):
    dims = np.shape(imgArray)
    circDiameter = circRad * 2
    # Calc number of lenses
    rowLenses = math.ceil(dims[0] / circDiameter)
    colLenses = math.ceil(dims[1] / circDiameter)
    return (rowLenses, colLenses)

# Extend imgArray to include a row at the bottom as the key
def extendImageForKey(imArray, bufferSize, circleRad, numKeyRows):
    imgDims = np.shape(imArray)
    # Put in some blank area between image and key
    bufferArray = np.full((bufferSize, imgDims[1], 3), RGB_BLACK, dtype=np.uint8) 
    keyRowArray = np.full((circleRad*2*numKeyRows, imgDims[1], 3), RGB_BLACK, dtype=np.uint8)
    extendedArr = np.vstack((imArray, bufferArray, keyRowArray))
    return extendedArr

# Determine how many rows of lenses we need to display the color palette
# Return the number of keys per row and number of rows
def calcNumKeyRows(imgWidth, numColors, circleRad):
    # Let's use 2/3 of the image width for the key
    keyRowWidth = math.ceil(imgWidth*KEY_WIDTH_TO_IMAGE_WIDTH)
    numKeysPerRow = math.floor(keyRowWidth/(circleRad*2))
    numRows = math.ceil(numColors/numKeysPerRow)
    return numRows, numKeysPerRow


### MAIN ###
# Inputs:
#   inImg - a PILLOW Image object
#   circleRad - the radius for the lenses to apply
# Outputs:
#    numpy ndarray in mxnx3, where third dimension is [R G B]
def main(inImg, circleRad, coloringBook, verbose):
    # Get a 2D array of the pixel (r,g,b) tuples
    imArray = np.asarray(inImg).copy() # copy so not readonly
    # Document the color palette of all colors in the image
    colorPalette, pixUniDims = np.unique(imArray.reshape(-1,3), axis=0, return_counts=True)
    if (verbose): print(f"Color Palette: {colorPalette}")

    # Find number of lenses spanning the height, width of the image
    numLensRows, numLensCols = getNumLenses(imArray, circleRad)
    lensArr = np.empty((numLensRows, numLensCols), dtype=object)

    # Populate lensArr by viewing the pixels which will fall under the lens
    # and documenting the window of pixels affected, the color mode, and the number
    # of this mode.
    print("CREATING LENSES...")
    for rowLens in trange(0,numLensRows):
        for colLens in range(0,numLensCols):
            # 1. Make a view of the pixels in the lensed area
            # pixels will be specified in (row,col) form
            tlPix = (rowLens*circleRad*2, colLens*circleRad*2)
            brPix = ((rowLens+1)*circleRad*2,(colLens+1)*circleRad*2)
            #print(f"tlPix {tlPix}, brPix {brPix}")
            imArrSection = imArray[tlPix[0]:brPix[0], tlPix[1]:brPix[1]]

            # 2. Flatten it and get the mode
            imArrSection = imArrSection.reshape(-1,3)
            sectionMode = PB.getMode(imArrSection)[0]
            if (verbose): print(f"SECTION: {rowLens,colLens}, MODE: {sectionMode}")

            # Capture the data for the lens
            modeNum = PB.findPixInList(sectionMode, colorPalette)
            lensArr[rowLens, colLens] = Lens(circleRad, tlPix, brPix, sectionMode, modeNum)

    # Given that all the lenses are the same size, we can just generate the inLens and outLens
    # masks for one of the lenses and reuse them over and over
    commonInLensMask = lensArr[0][0].genInLensMask()
    commonOutLensMask = lensArr[0][0].genOutLensMask()

    # Now we can go ahead and recolor the image by looking through all the lenses
    print("RECOLORING LENSES...")
    for currLens in tqdm(lensArr.flatten()):
        # Go ahead and grab a view of imArray so we can 0 index all our lens masks
        lensBoxView = imArray[currLens.tlPix[0]:currLens.brPix[0], currLens.tlPix[1]:currLens.brPix[1]]
        # Consider lensBoxView might be less than the size of a whole lens, and we
        # need to adjust the lens mask for that.
        boxViewDims = np.shape(lensBoxView)
        lensMaskDims = np.shape(commonInLensMask)
        #print(f"BOX DIMS: {boxViewDims}\nLENS DIMS: {lensMaskDims}")
        if (boxViewDims[0] == lensMaskDims[0] and boxViewDims[1] == lensMaskDims[1]):
            adjInLensMask = commonInLensMask
            adjOutLensMask = commonOutLensMask
        else:
            adjInLensMask = commonInLensMask[0:boxViewDims[0], 0:boxViewDims[1]]
            adjOutLensMask = commonOutLensMask[0:boxViewDims[0], 0:boxViewDims[1]]

        # Mask by what's in the lens and recolor
        if(coloringBook):
            lensBoxView[adjInLensMask] = RGB_WHITE
        else:    
            lensBoxView[adjInLensMask] = currLens.fillColor
        # Mask by what's out of the lens and recolor
        lensBoxView[adjOutLensMask] = RGB_BLACK

    # If doing a coloring book image, add the key row at the bottom
    # and then label the lenses with numbers
    if (coloringBook):
        # Add pixels to the bottom of the image for the key row
        bufferSize = 30
        numColors = len(colorPalette)
        imgWidth = np.shape(imArray)[1]
        numKeyRows, numKeysPerRow = calcNumKeyRows(imgWidth, numColors, circleRad)
        imArray = extendImageForKey(imArray, bufferSize, circleRad, numKeyRows)
        keyRowLenses = np.empty((numKeyRows,numKeysPerRow), dtype=object)
        # The key row will be centered, not beginning at left edge of image
        colOffset = math.ceil((imgWidth*(1-KEY_WIDTH_TO_IMAGE_WIDTH))/2)
        # Set up the lenses
        print("CREATING COLOR KEY...")
        for colorIter in trange(0,numColors):
            currentKeyRow = math.floor(colorIter/numKeysPerRow)
            keyIndexInRow = colorIter % numKeysPerRow
            tlPix = (np.shape(imArray)[0]-circleRad*2*(numKeyRows-currentKeyRow), colOffset+keyIndexInRow*circleRad*2)
            brPix = (tlPix[0]+circleRad*2, tlPix[1]+circleRad*2)
            keyRowLenses[currentKeyRow][keyIndexInRow] = Lens(circleRad, tlPix, brPix, colorPalette[colorIter], colorIter)

        # Color the key row
        for keyLens in keyRowLenses[keyRowLenses != None].flatten(): #ignore uninitialized lenses at end of key
            imArray[keyLens.tlPix[0]:keyLens.brPix[0], keyLens.tlPix[1]:keyLens.brPix[1]] = keyLens.fillColor

        # Do all the color number annotation
        imgForText = Image.fromarray(imArray)
        imgDraw = ImageDraw.Draw(imgForText)
        print("ANNOTATING COLOR NUMBERS...")
        for currLens in tqdm(lensArr.flatten()):
            # Number the lenses for the actual image
            centerCol = currLens.tlPix[1]+currLens.radius
            centerRow = currLens.tlPix[0]+currLens.radius
            # DRAW TAKES COL,ROW. Anchor the horizontal and vertical midpoints of the text on the given position
            imgDraw.text((centerCol, centerRow), str(currLens.fillNum), IMG_TEXT_COLOR, anchor="mm", font_size=8)
        for keyLens in keyRowLenses[keyRowLenses != None].flatten():
            # Number the lenses for the key row
            centerCol = keyLens.tlPix[1]+keyLens.radius
            centerRow = keyLens.tlPix[0]+keyLens.radius
            imgDraw.text((centerCol, centerRow), str(keyLens.fillNum), KEY_TEXT_COLOR, anchor="mm", font_size=8)
        
        # Update imArray to include all the annotation
        imArray = np.asarray(imgForText).copy()

    return imArray

# For execution as main module
if __name__ == "__main__":
    IMAGES_DIR = "./input_images"
    # Get user's arguments or defaults
    FILE_PATH, COLOR_THRESH, BLUR_OPT, LENS_SIZE, COLORING_BOOK, VERBOSE_MODE = TI.getInputArgs()
    if (FILE_PATH != None):
        FILE_PATH = Path(f"{IMAGES_DIR}/{FILE_PATH}")
    else:
        FILE_PATH = Path(f"{IMAGES_DIR}/burlington-sunset.jpg")
    
    print("### LENS MASK ###\n" \
        f"Lens Size: {LENS_SIZE}\n" \
        f"Coloring Book: {COLORING_BOOK}\n" \
        f"Selected Image: {FILE_PATH.name}")
    
    inImg = ImageOps.exif_transpose(Image.open(FILE_PATH))
    outArr = main(inImg, LENS_SIZE, COLORING_BOOK, VERBOSE_MODE)
    inImg.close()
    outImg = Image.fromarray(outArr)
    outImg.show()