#!/usr/bin/env python3
import sys
import logging
import pathlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""
Convert binary image to an I/O stream that can be used
by the DSP56k simulator to provide peripheral input.

An optional argument `repeat` allows you to repeat
each value multiple times.

Example for simulator:
 load program.lod
 input x:$FFFFC6 stream.io
"""

if len(sys.argv) < 3:
    logger.info("Usage: python3 %s <input_binary> <output_io> [repeat]", sys.argv[0])
    sys.exit(-1)

# Make sure the input file exists
src = pathlib.Path(sys.argv[1])
if not src.exists():
    logger.error("Input file %s does not exist!", src)
    sys.exit(-1)

# Check if repeat argument is a valid number
repeat = 1
if len(sys.argv) > 3:
    repeat = int(sys.argv[3], 10)

file_size = src.stat().st_size
if file_size % 3 != 0:
    logger.error("Expected a multiple of 24-bit words, size=%d", file_size)
    sys.exit(-1)

# Convert into IO
file_path = sys.argv[2]
with open(file_path, "wb") as lod:
    with open(sys.argv[1], "rb") as fp:
        for i in range(0, file_size // 3):
            w = int.from_bytes(fp.read(3), 'big')

            # Simulator supports #<number> suffix to repeat a value
            repeat_suffix = b""
            if repeat > 1:
                repeat_suffix = b"#%d" % repeat

            # Write the word
            lod.write(b'$%06x%s\n' % (w, repeat_suffix))

logger.info("Successfully wrote %s", file_path)
