# I want to automate and chain together the execution of pix_sort and
# lens_mask.py so I can just generate a bunch of images to view.
from pathlib import Path
from PIL import Image
import pix_sort as PS
import lens_mask as LM
import text_inputs as TI

# GLOBALS
IMAGE_FILES = []

if __name__=="__main__":
    IMAGES_DIR = "./input_images"
    OUTPUT_DIR = "./output_images"
    # Make the dir if it doesn't exist
    Path.mkdir(Path(OUTPUT_DIR), exist_ok=True) 

    # Get user's arguments or defaults
    FILE_PATH, COLOR_THRESH, BLUR_OPT, LENS_SIZE = TI.getInputArgs()
    
    # if no file specified, just use all
    if (FILE_PATH == None):
        # list all images in the inputs directory
        IMAGE_FILES = TI.getImagesInDir(IMAGES_DIR)
    else:
        IMAGE_FILES.append(Path(f"{IMAGES_DIR}/{FILE_PATH}"))

    print("### BOTTLECAP IMAGE PIPELINE ###\n" \
          f"Color Threshold: {COLOR_THRESH}\n" \
          f"Blur Option: {BLUR_OPT}\n" \
          f"Lens Size: {LENS_SIZE}\n"  \
          "Selected Images:")
    for img in IMAGE_FILES:
        print(f" - {img.name}")
        

    for fileName in IMAGE_FILES:
        print(f"\nFILE: {fileName}")
        inImg = Image.open(fileName)
        # Simplify the colors, save the new image
        threshSavePath = Path(f"{OUTPUT_DIR}/{fileName.stem}-thresh{COLOR_THRESH}.PNG")
        if Path(threshSavePath).is_file():
            print(f"{threshSavePath.name} exists") # file exists already
        else:
            outArr = PS.main(inImg, COLOR_THRESH, BLUR_OPT)
            outImg = Image.fromarray(outArr)
            outImg.save(threshSavePath,format='PNG')
            print(f"{threshSavePath.name} saved")

        # Do the lensing, save the new image
        lensSavePath = Path(f"{OUTPUT_DIR}/{fileName.stem}-thresh{COLOR_THRESH}-lens{LENS_SIZE}.PNG")
        if Path(lensSavePath).is_file():
            print(f"{lensSavePath.name} exists") # file exists already
        else:
            outArr = LM.main(outImg, LENS_SIZE)
            outImg = Image.fromarray(outArr)
            outImg.save(lensSavePath,format='PNG')
            print(f"{lensSavePath.name} saved")