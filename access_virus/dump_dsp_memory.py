#!/usr/bin/env python3
import io
import logging
import pathlib
import sys
from dataclasses import dataclass
from typing import Callable, List, Optional

import lib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PAD_CHAR = b'\0'  # padding used between non-consecutive sections in one region

"""
DSP memory dump utility for all Access Virus DSP command streams.

Usage: python3 dump_dsp_memory.py <cmd_stream_file> <output_file_prefix>

Writes P, X, Y memory regions for the Motorola DSP563xx. 

Can be used with command stream dumps made with `dump_bootstrap.py`.
This tool will mimic the bootstrapping done by the BootROM, and 
export the following files:

 output.p.bin: P memory
 output.x.bin: X memory
 output.y.bin: Y memory

All files will be written in big endian. Use `be2le.py` to convert to 
little endian for loading in IDA Pro.

Note: This command will overwrite existing output files.

Requires python version 3.8+.
"""

if len(sys.argv) != 3:
    logger.info("Usage: python3 %s <cmd_stream_file> <output_file_prefix>", sys.argv[0])
    sys.exit(-1)


@dataclass
class CommandHandler:
    region: str
    converter: Optional[Callable] = None

    def convert(self, value) -> List[int]:
        if self.converter:
            return self.converter(value)
        return [value]


def split_12bit(value) -> List[int]:
    val1 = value & 0xFFF000
    val2 = value << 0xC & 0xFFF000
    return [val1, val2]


# Make sure the input file exists
src = pathlib.Path(sys.argv[1])
if not src.exists():
    logger.error("Input file %s does not exist!", src)
    sys.exit(-1)

# Check if the file contains 24bit words
file_size = src.stat().st_size
if file_size % 3 != 0:
    logger.error("Expected a binary file with 24bit words!")
    sys.exit(-1)

# Read the 24bit words
with open(src, "rb") as fp:
    words = []
    for i in range(file_size // 3):
        words.append(int.from_bytes(fp.read(3), 'big'))

# Command handlers
handlers = {
    0: CommandHandler(region='p'),
    1: CommandHandler(region='x'),
    2: CommandHandler(region='y'),
    3: CommandHandler(region='y', converter=split_12bit),
}

commands = lib.get_dsp_commands(words)

# The last command should be 4, representing a jmp to the entrypoint
jump = commands.pop()
assert jump.cmd == 4, "Did you provide a valid command stream file?"
logger.info("Discovered entrypoint (command = 4) @ 0x%x", jump.addr)

# Sort the remaining commands by address to allow writing consecutively
commands = sorted(commands, key=lambda c: c.addr)

# Create a memory buffer for each region
buffers = {}
for region in ['p', 'x', 'y']:
    buffers[region] = io.BytesIO()

# Parse the commands
for cmd in commands:
    logger.debug("Writing command %d, addr=0x%06x, size=0x%06x", cmd.cmd, cmd.addr, cmd.size)
    handler = handlers.get(cmd.cmd)
    buffer = buffers.get(handler.region)
    buffer.write(PAD_CHAR * ((cmd.addr * 3) - buffer.tell()))  # write padding
    for word in cmd.data:
        values = handler.convert(word)
        for value in values:
            buffer.write(value.to_bytes(3, 'big'))

# Write the output files
for region, buffer in buffers.items():
    file_path = "%s.%s.be.bin" % (sys.argv[2], region)
    logger.info("Writing region %s to %s", region, file_path)
    buffer.seek(0)
    with open(file_path, "wb") as fp:
        fp.write(buffer.read())
    buffer.close()
