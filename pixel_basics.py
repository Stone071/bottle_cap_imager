# Just here to hold some shared functions for this stuff
import numpy as np
from PIL import Image

def ezDiff(a, b):
    if (a > b): return (a - b)
    elif (b > a): return (b - a)
    else: return 0

def getMode(arr):
    # Get the unique (r,g,b) tuples from 2d array
    uniqueVals, counts = np.unique(arr, axis=0, return_counts=True)
    # Get the mode tuple from counts and values
    mode = uniqueVals[np.argmax(counts)]
    return mode, max(counts)

def pixCompare(pixOne,pixTwo,threshold):
    if ((ezDiff(pixOne[0],pixTwo[0]) <= threshold)
        and (ezDiff(pixOne[1],pixTwo[1]) <= threshold)
        and (ezDiff(pixOne[2],pixTwo[2]) <= threshold)):
        return True
    else: return False

def sizeDown(img, desiredHeight):
    # Downsample the file. GIFs aren't mean to be high res.
    w, h = img.size
    scale_factor = desiredHeight/h
    w = int(w * scale_factor)
    h = desiredHeight
    downsize = img.resize((w,h), Image.LANCZOS)
    return downsize