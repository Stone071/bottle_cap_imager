###########################################################
# gif_pipeline.py
# 
# This pipeline performs image color simplification and lensing
# over a range of lenses, which are then composed into a single
# gif where the image appears to become clearer and then more
# obscure again.
#
# Zachary Stone, February 2026
###########################################################
from pathlib import Path
from PIL import Image, ImageOps
import pix_sort as PS
import lens_mask as LM
import pixel_basics as PB
import text_inputs as TI

# GLOBALS
IMAGE_FILES = []
LENS_RADII = [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]

# Generate all the frames of the gif in order and return them in a list
def makeGif(numLenses, inImg):
    gifFrames = [0] * (numLenses * 2 + 1) # empty list
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

# For execution as main module
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
        print(f"\nPROCESSING FILE: {fileName}")
        saveDir = Path("./output_gifs")
        # Make the dir if it doesn't exist
        Path.mkdir(saveDir, exist_ok=True) 
        # Open image and rotate if exif data specifies so
        origImg = ImageOps.exif_transpose(Image.open(fileName))
        # Downsample the file. GIFs aren't mean to be high res.
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
        print(f"\nSAVING FILE: {outGif}")
        gifFrames[0].save(
            outGif,
            save_all=True,
            append_images=gifFrames[1:],
            duration=200, #milliseconds
            loop=0,
            optimize=False
        )

        for i in range(0,len(gifFrames)): gifFrames[i].close()