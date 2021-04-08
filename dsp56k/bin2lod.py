#!/usr/bin/env python3
import sys
import logging
import pathlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""
Convert binary image to an OMF file that can be loaded
by the DSP56k simulator as source binary.
"""

if len(sys.argv) < 3:
    logger.info("Usage: python3 %s <input_binary> <output_lod> [hex_offset]", sys.argv[0])
    sys.exit(-1)

# Make sure the input file exists
src = pathlib.Path(sys.argv[1])
if not src.exists():
    logger.error("Input file %s does not exist!", src)
    sys.exit(-1)

# Check the offset
offset = 0
if len(sys.argv) > 3:
    offset = int(sys.argv[3], 16)

file_size = src.stat().st_size
if file_size % 3 != 0:
    logger.error("Expected a multiple of 24-bit words, size=%d", file_size)
    sys.exit(-1)

# Convert into OMF
file_path = sys.argv[2]
with open(file_path, "wb") as lod:
    lod.write(b'_DATA P %06x\n' % offset)
    with open(sys.argv[1], "rb") as fp:
        for i in range(0, file_size // 3):
            w = int.from_bytes(fp.read(3), 'big')
            lod.write(b'%06x ' % w)
            if (i + 1) % 8 == 0:
                lod.write(b'\n')
        lod.write(b'\n\n')
    lod.write(b'_END 000000\n')

logger.info("Successfully wrote %s", file_path)
