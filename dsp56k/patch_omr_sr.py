#!/usr/bin/env python3
import logging
import pathlib
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OMR_MASK = 0xffffff ^ 0x4000  # disable address priority
SR_MASK = 0xffffff ^ 0x80000  # disable instruction cache

"""
Binary patch utility for DSP56k binary files.

This utility will change the instructions that change the OMR
and SR register so that the Motorola Simulator will work
properly. 

Usage: python3 patch_omr_sr.py <binary_file> <output_file>

"""

if len(sys.argv) != 3:
    logger.info("Usage: python3 %s <binary_file> <output_file>", sys.argv[0])
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

# Instruction mapping
OMR = b"\x05\xf4\x3a"  # move OP,omr
SR = b"\x05\xf4\x39"   # move OP,sr

file_path = pathlib.Path(sys.argv[2])
with open(file_path, "wb") as output:
    with open(src, "rb") as fp:
        while fp.tell() < file_size:
            word = fp.read(3)
            if word == OMR:
                # Patch OMR
                operand = int.from_bytes(fp.read(3), 'big')
                patch = operand & OMR_MASK
                output.write(word)
                output.write(patch.to_bytes(3, 'big'))
                logger.info("Patched OMR from 0x%06x to 0x%06x", operand, patch)
            elif word == SR:
                # Patch SR
                operand = int.from_bytes(fp.read(3), 'big')
                patch = operand & SR_MASK
                output.write(word)
                output.write(patch.to_bytes(3, 'big'))
                logger.info("Patched SR from 0x%06x to 0x%06x", operand, patch)
            else:
                # Nothing to do, just forward the input data
                output.write(word)

logger.info("Successfully wrote %s", file_path)
