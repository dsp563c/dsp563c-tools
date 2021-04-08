import logging
import os
import sys

from chunks import get_chunks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""
Extraction tool for VirusTI vti bin files.

Usage: python3 firmware.py <vti file> <output folder>

Can be used with vti.bin, vti2.bin and vti_snow.bin which
can be extracted from the Virus TI installation media
using firmware.py.

Known issue:
With vti_2.bin, the extraction tool does not work properly
for the P.bin ROM. It seems that it uses a different format,
maybe concatenating the files will be sufficient.
The F.bin and S.bin can still be extracted though.
"""


if len(sys.argv) != 3:
    logger.info("Usage: python3 %s <input firmware> <output folder>", sys.argv[0])
    sys.exit(-1)

logger.info("Opening vti file %s", sys.argv[1])

# Create output folder
try:
    os.mkdir(sys.argv[2])
except FileExistsError:
    logger.error("Output folder %s already exists", sys.argv[2])
    sys.exit(-1)

# Parse chunks from firmware file
with open(sys.argv[1], "rb") as fp:
    chunks = get_chunks(fp)

# Extract the different ROMs
for rom_prefix in ['F', 'S', 'P']:
    parts = [c for c in chunks if c.name.startswith(rom_prefix)]
    if not parts:
        logger.debug("Skipping not included ROM %s.bin", rom_prefix)
        continue

    output = b''
    for chunk in parts:
        assert chunk.size % 0x23 == 2  # 2 bytes extra at the end (checksum?)
        logger.debug("Processing chunk %s", chunk.name)
        idx = 0
        for i in range(0, chunk.size - 2, 0x23):
            int.from_bytes(chunk.data[i:i+1], 'big')  # chunk id?
            header = int.from_bytes(chunk.data[i+1:i+3], 'big')
            assert idx == header
            output += chunk.data[i+3:i+0x23]
            idx += 32

    output_path = "%s/%s.bin" % (sys.argv[2], rom_prefix)
    with open(output_path, "wb") as fpout:
        fpout.write(output)

    logger.info("Successfully wrote ROM to %s", output_path)
