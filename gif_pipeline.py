# I want to create a specific pipeline to generate cool gifs where the
# images become clearer and then more obscure again.
from pathlib import Path
from PIL import Image
import sys
import pix_sort as PS
import lens_mask as LM
import pixel_basics as PB
import text_inputs as TI

# GLOBALS
IMAGE_FILES = []
THRESHOLDS = [15,20,30,40,50,127,150]
LENS_RADII = [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]


def makeGif(numLenses, inImg):
    gifFrames = [None] * (numLenses * 2 + 1) # empty list
    for i in range(0,numLenses):
        # Do the lensing, save the frames for the gif
        frameA = numLenses-i-1
        frameB = numLenses+i+1
        outArr = LM.main(inImg, LENS_RADII[i])
        outImg = Image.fromarray(outArr)
        # add frames to list
        if (i == 0): gifFrames[numLenses] = outImg
        gifFrames[frameA] = outImg
        gifFrames[frameB] = outImg
    return gifFrames

if __name__=="__main__":
    IMAGES_DIR = "./input_images"
    # Get user's arguments or defaults
    FILE_PATH, COLOR_THRESH, BLUR_OPT, LENS_SIZE = TI.getInputArgs()
    
    # if no file specified, just use all
    if (FILE_PATH == None):
        # list all images in the inputs directory
        IMAGE_FILES = TI.getImagesInDir(IMAGES_DIR)
    else:
        IMAGE_FILES.append(Path(f"{IMAGES_DIR}/{FILE_PATH}"))

    print("### BOTTLECAP GIF PIPELINE ###\n" \
          f"Color Threshold: {COLOR_THRESH}\n" \
          f"Blur Option: {BLUR_OPT}\n" \
          "Selected Images:")
    for img in IMAGE_FILES:
        print(f" - {img.name}")
        

    for fileName in IMAGE_FILES:
        print(f"\nFILE: {fileName}")
        saveDir = Path("./output_gifs")
        # Make the dir if it doesn't exist
        Path.mkdir(saveDir, exist_ok=True) 
        # Downsample the file. GIFs aren't mean to be high res.
        origImg = Image.open(fileName)
        downsize = PB.sizeDown(origImg, 768)
        # Don't forget to close these things
        origImg.close()

        # Simplify the colors, save the new image
        outArr = PS.main(downsize, COLOR_THRESH, BLUR_OPT)
        simpleColorImg = Image.fromarray(outArr)

        # Make a list of frames
        numLenses = len(LENS_RADII)
        gifFrames = makeGif(numLenses, simpleColorImg)
        simpleColorImg.close()
        
        # Generate the gif from the frames
        outGif = f"{saveDir}/{fileName.stem}.gif"
        gifFrames[0].save(
            outGif,
            save_all=True,
            append_images=gifFrames[1:],
            duration=200, #milliseconds
            loop=0,
            optimize=False
        )

        for i in range(0,len(gifFrames)): gifFrames[i].close()