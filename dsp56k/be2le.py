#!/usr/bin/env python3
import sys
import logging
import pathlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""
Convert big endian to little endian for 24bit files.
"""

if len(sys.argv) != 3:
    logger.info("Usage: python3 %s <input_binary> <output_binary>", sys.argv[0])
    sys.exit(-1)

# Make sure the input file exists
src = pathlib.Path(sys.argv[1])
if not src.exists():
    logger.error("Input file %s does not exist!", src)
    sys.exit(-1)

file_size = src.stat().st_size
if file_size % 3 != 0:
    logger.error("Expected a multiple of 24-bit words, size=%d", file_size)
    sys.exit(-1)

# Convert into little endian
file_path = sys.argv[2]
with open(file_path, "wb") as output:
    with open(sys.argv[1], "rb") as fp:
        for i in range(0, file_size // 3):
            word = int.from_bytes(fp.read(3), 'big')
            output.write(word.to_bytes(3, 'little'))

logger.info("Successfully wrote %s", file_path)
