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
class Lens:
    radius = 0
    diameter = 0
    tlPix = (0,0)
    brPix = (0,0)
    fillColor = (0,0,0)
    fillNum = 255
    inLensMask = None
    outLensMask = None
    perimeterLensMask = None
    perimeterWidth = 1

    def __init__(self, radius, tlPix, brPix, fillColor, fillNum):
        self.radius = radius
        self.diameter = int(2*radius)
        self.tlPix = tlPix # (row, column)
        self.brPix = brPix # (row, column)
        self.fillColor = fillColor # [R G B]
        self.fillNum = fillNum # The number associated with this color    
        self.inLensMask = np.zeros((self.diameter, self.diameter), dtype=bool)
        self.outLensMask = np.zeros((self.diameter, self.diameter), dtype=bool)
        self.perimeterLensMask = np.zeros((self.diameter,self.diameter), dtype=bool)

    def setInLensMask(self, arr):
        self.inLensMask = arr

    def setOutLensMask(self, arr):
        self.outLensMask = arr

    def setPerimeterLensMask(self, arr):
        self.perimeterLensMask = arr

    def genInLensMask(self, forceGen=False):
        # Skip execution if already generated
        if (self.inLensMask.any() and forceGen == False):
            return self.inLensMask
        # Check valid radius
        elif (self.radius > 0):
            for m in range(0,self.diameter):
                for n in range(0, self.diameter):
                    # just use a^2 + b^2 = r^2 generate the mask, where the "origin" is at self.radius
                    # since 0,0 is the top left hand corner
                    sqDist = (PB.ezDiff(m, self.radius)**2 + PB.ezDiff(n,self.radius)**2)
                    if (sqDist < (self.radius)**2):
                        self.inLensMask[m,n] = True
                    else:
                        self.inLensMask[m,n] = False
            return self.inLensMask
        # return error
        else:
            return -1

    def genPerimeterLensMask(self):
        if (self.radius > 0):
            for m in range(0,self.diameter):
                for n in range(0, self.diameter):
                    sqDist = (PB.ezDiff(m, self.radius)**2 + PB.ezDiff(n,self.radius)**2)
                    if (sqDist >= (self.radius)**2) and (sqDist <= (self.radius+self.perimeterWidth)**2):
                        self.perimeterLensMask[m,n] = True
                    else:
                        self.perimeterLensMask[m,n] = False
            return self.perimeterLensMask

    def genOutLensMask(self):
        # Check if array is already populated
        if (self.inLensMask.any()):
            self.outLensMask = ~self.inLensMask
        else:
            self.genInLensMask()
            self.outLensMask = ~self.inLensMask
        return self.outLensMask