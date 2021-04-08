#!/usr/bin/env python3
import logging
import pathlib
import sys

import lib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""
Extraction utility for all Access Virus EEPROM flash dumps.

Usage: python3 dump_bootstrap.py <flash_file> <output_file_prefix>
  
Can be used with flash memory dumps of any Access Virus model.
This tool will export both the DSP BootROM as well as the CommandStream
data that the BootROM will use to initialize DSP P, X and Y memory.

The BootROM stream file uses the following format that the DSP563xx chip 
accepts to write the BootROM to the given offset in program memory:
[ size ] [ offset ] [ data ... ]

Resulting files:
 output.bootrom.be.bin: BootROM only
 output.bootrom_stream.be.bin: BootROMStream (including size,offset header)
 output.command_stream.be.bin: CommandStream (used by the BootROM)
 
The last file can be used as input for `dump_dsp_memory.py`.
 
All files will be written in big endian. Use `be2le.py` to convert to 
little endian for loading in IDA Pro.

Note: This command will overwrite existing output files.

Requires python version 3.8+.
"""

if len(sys.argv) != 3:
    logger.info("Usage: python3 %s <flash_file> <output_file_prefix>", sys.argv[0])
    sys.exit(-1)

# Make sure the input file exists
src = pathlib.Path(sys.argv[1])
if not src.exists():
    logger.error("Input file %s does not exist!", src)
    sys.exit(-1)

# Find the model type based on the file size
file_size = src.stat().st_size
model_type = lib.AccessVirusType.from_size(file_size)
if not model_type:
    logger.error("Could not determine Access Virus model type for file size %sK", file_size // 1024)
    sys.exit(-1)

# Parse the banks that contain DSP code/data
with open(src, "rb") as fp:
    bank_data = lib.get_dsp_bank_data(fp, model_type)

logger.info("Flash version: %s, Size: 0x%x", bank_data.version, len(bank_data.data))

# Parse the bank data into BootROM and CommandStream
chunk_data = lib.get_dsp_chunk_data(bank_data)
logger.info("BootROM size: 0x%x", chunk_data.bootrom_size)
logger.info("BootROM offset: 0x%x", chunk_data.bootrom_offset)
logger.info("CommandStream size: 0x%x", len(chunk_data.data))

# Write BootROM
file_path = "%s.bootrom.be.bin" % sys.argv[2]
with open(file_path, "wb") as fp:
    for word in chunk_data.bootrom_data:
        fp.write(word.to_bytes(3, 'big'))

logger.info("Successfully wrote BootROM to %s", file_path)

# Write BootROMStream
file_path = "%s.bootrom_stream.be.bin" % sys.argv[2]
with open(file_path, "wb") as fp:
    fp.write(chunk_data.bootrom_size.to_bytes(3, 'big'))
    fp.write(chunk_data.bootrom_offset.to_bytes(3, 'big'))
    for word in chunk_data.bootrom_data:
        fp.write(word.to_bytes(3, 'big'))

logger.info("Successfully wrote BootROMStream to %s", file_path)

# Write CommandStream
file_path = "%s.command_stream.be.bin" % sys.argv[2]
with open(file_path, "wb") as fp:
    for word in chunk_data.data:
        fp.write(word.to_bytes(3, 'big'))  # BootROM expects data in big endian

logger.info("Successfully wrote CommandStream to %s", file_path)
