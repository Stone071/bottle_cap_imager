###########################################################
# lens_class.py
# 
# This file just defines a class lens which is used in lens_mask.py
# for modifying images.
#
# Zachary Stone, July 2026
###########################################################
### IMPORTS
import numpy as np
import pixel_basics as PB

### CLASSES
# In this lens we use (row,col) coordinates to specify top left and bottom
# right pixel of the lens's bounding box. It also has a radius and (R,G,B) fill
class lens:
    radius = 0
    tlPix = (0,0)
    brPix = (0,0)
    fillColor = (0,0,0)
    fillNum = 255
    inLensMask = None
    outLensMask = None

    def __init__(self, radius, tlPix, brPix, fillColor, fillNum):
        self.radius = radius
        self.tlPix = tlPix # (row, column)
        self.brPix = brPix # (row, column)
        self.fillColor = fillColor # [R G B]
        self.fillNum = fillNum # The number associated with this color    
        self.inLensMask = np.zeros((radius*2, radius*2), dtype=bool)
        self.outLensMask = np.zeros((radius*2, radius*2), dtype=bool)

    def setInLensMask(self, arr):
        self.inLensMask = arr

    def setOutLensMask(self, arr):
        self.outLensMask = arr

    def genInLensMask(self, forceGen=False):
        # Skip execution if already generated
        if (self.inLensMask.any() and forceGen == False):
            return self.inLensMask
        # Check valid radius
        elif (self.radius > 0):
            for m in range(0,self.radius*2):
                for n in range(0, self.radius*2):
                    # just use a^2 + b^2 = r^2 generate the mask
                    sqDist = (PB.ezDiff(m, self.radius)**2 + PB.ezDiff(n,self. radius)**2)
                    if (sqDist <= self.radius**2):
                        self.inLensMask[m,n] = True
                    else:
                        self.inLensMask[m,n] = False
            return self.inLensMask
        # return error
        else:
            return -1

    def genOutLensMask(self):
        # Check if array is already populated
        if (self.inLensMask.any()):
            self.outLensMask = ~self.inLensMask
        else:
            self.genInLensMask()
            self.outLensMask = ~self.inLensMask
        return self.outLensMask