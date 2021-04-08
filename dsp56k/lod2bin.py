#!/usr/bin/env python3
import sys
import logging
import pathlib
from dataclasses import dataclass
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PAD_CHAR = b'\0'  # padding used between non-consecutive sections in one region

"""
Convert an OMF file into a binary image that can be loaded
into a disassembler.

Will create files for each region that exists in the OMF.
"""

if len(sys.argv) != 3:
    logger.info("Usage: python3 %s <input_lod> <output_prefix>", sys.argv[0])
    sys.exit(-1)


@dataclass
class Section:
    name: str
    offset: int
    data: List[int]


# Make sure the input file exists
src = pathlib.Path(sys.argv[1])
if not src.exists():
    logger.error("Input file %s does not exist!", src)
    sys.exit(-1)

# Parse all the sections
sections = []
with open(sys.argv[1], "rb") as fp:
    lines = fp.read().decode().split("\n")

    section = None
    for line in lines:
        line = line.strip()
        if not line:
            continue  # skip empty lines

        if line.startswith("_"):
            if section:
                # Flush previous section
                sections.append(section)

            # Section start
            if line.startswith("_DATA"):
                _, name, offset = line.split(" ")
                section = Section(name, int(offset, 16), [])
        else:
            words = line.split(" ")
            for word in words:
                assert 0 < len(word) <= 6
                section.data.append(int(word, 16))

# Get unique section names
section_names = set([s.name for s in sections])
for name in section_names:
    subsections = sorted([s for s in sections if s.name == name], key=lambda s: s.offset)

    file_path = "%s.%s.bin" % (sys.argv[2], name)
    with open(file_path, "wb") as fp:
        for section in subsections:
            logger.info("Section %s, offset=0x%x, size=0x%x", section.name, section.offset, len(section.data))
            fp.write(PAD_CHAR * ((section.offset * 3) - fp.tell()))  # write padding
            print('0x%x' % fp.tell())
            for word in section.data:
                fp.write(word.to_bytes(3, 'big'))

    logger.info("Successfully wrote %s", file_path)
