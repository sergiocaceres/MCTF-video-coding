#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

# Texture compression. Constant quantization of temporal subbands.

import os
import sys
import display
import math
from GOP import GOP
from subprocess import check_call
from subprocess import CalledProcessError
from arguments_parser import arguments_parser
import logging

logging.basicConfig()
log = logging.getLogger("texture_compress__constant")

parser = arguments_parser(description="Compress the texture.")
parser.GOPs()
parser.pixels_in_x()
parser.pixels_in_y()
parser.layers()
#parser.quantization()
#parser.quantization_step()
#parser.quantization_max()
#parser.quantization_min()
parser.quality()
parser.TRLs()
parser.SRLs()

args = parser.parse_known_args()[0]
GOPs = int(args.GOPs); log.debug("GOPs={}".format(GOPs))
layers = int(args.layers)
pixels_in_x = int(args.pixels_in_x)
pixels_in_y = int(args.pixels_in_y)
layers = int(args.layers)
#quantization = int(args.quantization)
#quantization_step = int(args.quantization_step)
#quantization_max = int(args.quantization_max)
#quantization_min = int(args.quantization_min)
quality = float(args.quality)
TRLs = int(args.TRLs)
SRLs = int(args.SRLs)

MCTF_TEXTURE_CODEC   = os.environ["MCTF_TEXTURE_CODEC"]
HIGH                 = "high"
LOW                  = "low"

# Slope computation
MAX_SLOPE = 50000
MIN_SLOPE = 40000
RANGE_SLOPES = MAX_SLOPE - MIN_SLOPE

slope = int(round(MAX_SLOPE - RANGE_SLOPES*quality))
if slope < 0:
    slope = 0

gop      = GOP()
GOP_size = gop.get_size(TRLs)

pictures = (GOPs - 1) * GOP_size + 1

'''
slopes = []
for i in range(layers):
    slopes.append(quantization + i*quantization_step)

if len(slopes) == 1:
    str_slopes = str(slopes[0])
else:
    str_slopes = ','.join(str(i) for i in slopes)
'''

# Compression of HIGH frequency temporal subbands.
subband = 1
while subband < TRLs:
    pictures = (pictures + 1) // 2
    command = "mctf subband_texture_compress__" + MCTF_TEXTURE_CODEC \
      + " --file="              + HIGH + "_" + str(subband) \
      + " --layers="            + str(layers) \
      + " --pictures="          + str(pictures - 1) \
      + " --pixels_in_x="       + str(pixels_in_x) \
      + " --pixels_in_y="       + str(pixels_in_y) \
      + " --slope=\""           + str(slope) + "\"" \
      + " --SRLs="              + str(SRLs)
    log.debug("command={}".format(command))
    try:
        check_call(command, shell=True)
    except CalledProcessError:
        sys.exit(-1)

    subband += 1

# Compression of LOW frequency temporal subband.
command = "mctf subband_texture_compress__" + MCTF_TEXTURE_CODEC \
  + " --file="              + LOW + "_" + str(TRLs - 1) \
  + " --layers="            + str(layers) \
  + " --pictures="          + str(pictures) \
  + " --pixels_in_x="       + str(pixels_in_x) \
  + " --pixels_in_y="       + str(pixels_in_y) \
  + " --slope=\""           + str(slope) + "\""\
  + " --SRLs="              + str(SRLs)
log.debug(command)
try:
    check_call(command, shell=True)
except:
    sys.exit(-1)
