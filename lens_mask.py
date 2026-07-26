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
from lens_class import lens
from pathlib import Path

### GLOBALS
RGB_WHITE = (255,255,255)
RGB_BLACK = (0,0,0)

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
# NOTE: It's possible we will have enough colors that one row won't be enough room
def extendImageForKey(imArray, circleRad):
    imgDims = np.shape(imArray)
    #print(f"Orig array dims: {imgDims[0]} {imgDims[1]} {imgDims[2]}")
    keyRowArray = np.full((circleRad*2, imgDims[1], 3), RGB_BLACK, dtype=np.uint8)
    extendedArr = np.vstack((imArray, keyRowArray))
    return extendedArr

### MAIN ###
# Inputs:
#   inImg - a PILLOW Image object
#   circleRad - the radius for the lenses to apply
# Outputs:
#    numpy ndarray in mxnx3, where third dimension is [R G B]
def main(inImg, circleRad, coloringBook):
    # Get a 2D array of the pixel (r,g,b) tuples
    imArray = np.asarray(inImg).copy() # copy so not readonly
    # Document the color palette of all colors in the image
    colorPalette, pixUniDims = np.unique(imArray.reshape(-1,3), axis=0, return_counts=True)
    #print(f"Color Palette: {colorPalette}")

    # Find number of lenses spanning the height, width of the image
    numLensRows, numLensCols = getNumLenses(imArray, circleRad)
    lensArr = np.empty((numLensRows, numLensCols), dtype=object)

    # Populate lensArr by viewing the pixels which will fall under the lens
    # and documenting the window of pixels affected, the color mode, and the number
    # of this mode.
    for rowLens in range(0,numLensRows):
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
            #print(f"SECTION: {rowLens,colLens}, MODE: {sectionMode}")

            # Capture the data for the lens
            modeNum = PB.findPixInList(sectionMode, colorPalette)
            lensArr[rowLens, colLens] = lens(circleRad, tlPix, brPix, sectionMode, modeNum)

    # Given that all the lenses are the same size, we can just generate the inLens and outLens
    # masks for one of the lenses and reuse them over and over
    commonInLensMask = lensArr[0][0].genInLensMask()
    commonOutLensMask = lensArr[0][0].genOutLensMask()

    # Now we can go ahead and recolor the image by looking through all the lenses
    for currLens in lensArr.flatten():
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
        # Color in the key row
        startRow = np.shape(imArray)[0]
        endRow = startRow + circleRad*2
        startCol = 0
        endCol = startCol + circleRad*2
        imArray = extendImageForKey(imArray, circleRad)
        # NOTE: Consider at some point that we may have more key colors than fit on one line
        keyRowLenses = np.empty((1,numLensCols), dtype=object)
        # paint the key row the appropriate colors
        for colorIter in range(0,len(colorPalette)):
            imArray[startRow:endRow, startCol:endCol] = colorPalette[colorIter]
            # Make some key row lenses for easy numbering
            keyRowLenses[0][colorIter] = lens(circleRad,(startRow,startCol),(endRow,endCol),
                                           colorPalette[colorIter], colorIter)
            startCol = endCol
            endCol += circleRad*2

        # Do all the color number annotation
        imgForText = Image.fromarray(imArray)
        imgDraw = ImageDraw.Draw(imgForText)
        for currLens in lensArr.flatten():
            # Number the lenses for the actual image
            centerCol = currLens.tlPix[1]+currLens.radius
            centerRow = currLens.tlPix[0]+currLens.radius
            # DRAW TAKES COL,ROW. Anchor the horizontal and vertical midpoints of the text on the given position
            imgDraw.text((centerCol, centerRow), str(currLens.fillNum), RGB_BLACK, anchor="mm", font_size=8)
        for keyLens in keyRowLenses[keyRowLenses != None].flatten(): # mask off the lenses which are not populated
            # Number the lenses for the key row
            centerCol = keyLens.tlPix[1]+keyLens.radius
            centerRow = keyLens.tlPix[0]+keyLens.radius
            imgDraw.text((centerCol, centerRow), str(keyLens.fillNum), RGB_WHITE, anchor="mm", font_size=8)
        
        # Update imArray to include all the annotation
        imArray = np.asarray(imgForText).copy()

    return imArray

# For execution as main module
if __name__ == "__main__":
    IMAGES_DIR = "./input_images"
    # Get user's arguments or defaults
    FILE_PATH, COLOR_THRESH, BLUR_OPT, LENS_SIZE, COLORING_BOOK = TI.getInputArgs()
    if (FILE_PATH != None):
        FILE_PATH = Path(f"{IMAGES_DIR}/{FILE_PATH}")
    else:
        FILE_PATH = Path(f"{IMAGES_DIR}/burlington-sunset.jpg")
    
    print("### LENS MASK ###\n" \
        f"Lens Size: {LENS_SIZE}\n" \
        f"Coloring Book: {COLORING_BOOK}\n" \
        f"Selected Image: {FILE_PATH.name}")
    
    inImg = ImageOps.exif_transpose(Image.open(FILE_PATH))
    outArr = main(inImg, LENS_SIZE, COLORING_BOOK)
    inImg.close()
    outImg = Image.fromarray(outArr)
    outImg.show()