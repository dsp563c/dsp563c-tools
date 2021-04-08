import logging
import os
import sys

from chunks import get_chunks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""
Extraction tool for VirusTI firmware files.

Usage: python3 firmware.py <firmware file> <output folder>

Can be used with firmware_bin and firmware_bin64 from
Virus TI installation media.
"""


if len(sys.argv) != 3:
    logger.info("Usage: python3 %s <input firmware> <output folder>", sys.argv[0])
    sys.exit(-1)

logger.info("Opening firmware file %s", sys.argv[1])

# Create output folder
try:
    os.mkdir(sys.argv[2])
except FileExistsError:
    logger.error("Output folder %s already exists", sys.argv[2])
    sys.exit(-1)

# Parse chunks from firmware file
with open(sys.argv[1], "rb") as fp:
    chunks = get_chunks(fp)

# Get file table
tables = [c for c in chunks if c.name == "TABL"]
if not tables:
    logger.error("TABL not found, did you supply a firmware file?")
    sys.exit(-1)

# Parse file table
tabl = tables[0]
count = tabl.data[0]
entries = [e.decode() for e in tabl.data[1:].split(b"\0") if e]
assert len(entries) == count

# Write entries to files
for idx, entry in enumerate(entries):
    logger.info("Writing entry %s", entry)
    chunk = chunks[idx+1]
    with open("%s/%s" % (sys.argv[2], entry), "wb") as fpout:
        fpout.write(chunk.data)

logger.info("Successfully wrote chunks to folder %s", sys.argv[2])
