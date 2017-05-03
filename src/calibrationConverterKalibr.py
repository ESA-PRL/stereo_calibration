#!/usr/bin/env python

"""
This script converts the calibration output from Kalibr and
formats it in the proper way for the ROCK stereo configuration.

The cameras are assumed to be in the following order:
cam0: BB2 left
cam1: BB2 right
cam2: BB3 left
cam3: BB3 center
cam4: BB3 right
cam5: pancam left
cam6: pancam right

The transformation from quaternions to Euler angles is done using
Christoph Gohlkes transformations.py.
"""

__author__ = "Levin Gerdes"

import yaml
import re
import numpy as np
import os.path
from decimal import *
from Tkinter import Tk
from tkFileDialog import askopenfilename
from transformations import euler_from_quaternion

# precision for Decimal
getcontext().prec = 16

## Ask for calibration results
print("Please choose the files containing the Kalibr calibration output\n")
#Tk().withdraw()
calibResults = askopenfilename(title="Locate results-cam-kalibr.txt",
                                   initialdir="~/Desktop")
camChain = askopenfilename(title="Locate camchain-kalibr.yaml",
                                   initialdir="~/Desktop")

# kalibrs output files
#camChain = 'camchain-kalibr.yaml'
#calibResults = 'results-cam-kalibr.txt'

f = open(camChain)
fCamChain = f.read()
f.close()
data = yaml.load(fCamChain)

fxLeft    = data['cam5']['intrinsics'][0]
fyLeft    = data['cam5']['intrinsics'][1]
cxLeft    = data['cam5']['intrinsics'][2]
cyLeft    = data['cam5']['intrinsics'][3]
widthL    = data['cam5']['resolution'][0]
heightL   = data['cam5']['resolution'][1]
distLeft  = data['cam5']['distortion_coeffs']

fxRight   = data['cam6']['intrinsics'][0]
fyRight   = data['cam6']['intrinsics'][1]
cxRight   = data['cam6']['intrinsics'][2]
cyRight   = data['cam6']['intrinsics'][3]
width     = data['cam6']['resolution'][0]
height    = data['cam6']['resolution'][1]
distRight = data['cam6']['distortion_coeffs']

if (int(width) != int(widthL) or int(height) != int(heightL)):
    print('Dimensions of left and right pancam do not fit or the cameras have been reordered. Aborting!')
    quit()

print("\nCALIBRATION CONVERSION.\nThis script does not write anything to disk.\n")

# Extrinsics
f = open(calibResults, 'r')
fCalibResults = f.read()
f.close()

reExtrinsics = '(?<=baseline T_6_5\:\n)(.*)\n(.*)'
extrinsics = re.search(reExtrinsics, fCalibResults).group(0)
quaternions = re.search('(?<=q\:\s\[)(\s*-?\d+.\d+){4}', extrinsics).group(0).split()
translation = re.search('(?<=t\:\s\[)(\s*-?\d+.\d+){3}', extrinsics).group(0).split()
quaternions = np.array(quaternions).astype(np.float)
translation = np.array(translation).astype(np.float)*1e3 # ROCK needs the values in mm instead of meters
tx,ty,tz = translation

euler = euler_from_quaternion(quaternions, 'sxyz')
# does it need to be flipped?
#euler = np.array(euler).astype(np.float)*(-1)

# PRINT RESULTS
res =  "\nstereoCameraCalibration:"
res += "\n  camLeft:"
res += "\n    fx: " + str(fxLeft)
res += "\n    fy: " + str(fyLeft)
res += "\n    cx: " + str(cxLeft)
res += "\n    cy: " + str(cyLeft)
res += "\n    d0: " + str(distLeft[0])
res += "\n    d1: " + str(distLeft[1])
res += "\n    d2: " + str(distLeft[2])
res += "\n    d3: " + str(distLeft[3])
res += "\n    width: " + str(width)
res += "\n    height: " + str(height)
res += "\n    ex: 0"
res += "\n    ey: 0"
res += "\n  camRight:"
res += "\n    fx: " + str(fxRight)
res += "\n    fy: " + str(fyRight)
res += "\n    cx: " + str(cxRight)
res += "\n    cy: " + str(cyRight)
res += "\n    d0: " + str(distRight[0])
res += "\n    d1: " + str(distRight[1])
res += "\n    d2: " + str(distRight[2])
res += "\n    d3: " + str(distRight[3])
res += "\n    width: " + str(width)
res += "\n    height: " + str(height)
res += "\n    ex: 0.0"
res += "\n    ey: 0.0"
res += "\n#Distance between left and right camera"
res += "\n  extrinsic:"
res += "\n    tx: " + str(1*Decimal(tx))
res += "\n    ty: " + str(1*Decimal(ty))
res += "\n    tz: " + str(1*Decimal(tz))
res += "\n    rx: " + str(1*Decimal(euler[0]))
res += "\n    ry: " + str(1*Decimal(euler[1]))
res += "\n    rz: " + str(1*Decimal(euler[2]))

print(res)