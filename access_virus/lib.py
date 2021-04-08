import enum
import logging
from dataclasses import dataclass
from typing import BinaryIO, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class DSPBankData:
    version: str
    data: List[int]


@dataclass
class DSPChunkData:
    bootrom_size: int
    bootrom_offset: int
    bootrom_data: List[int]
    data: List[int]


@dataclass
class DSPCommandData:
    cmd: int
    addr: int
    size: Optional[int]
    data: Optional[List[int]]


@dataclass
class AccessVirusSpec:
    size: int
    dsp_offset: int

    def matches_size(self, size: int):
        return size == self.size


class AccessVirusType(enum.Enum):
    LEGACY = AccessVirusSpec(size=512*1024, dsp_offset=0x18000)
    TI = AccessVirusSpec(size=1024*1024, dsp_offset=0x70000)

    @classmethod
    def from_size(cls, size: int) -> Optional['AccessVirusType']:
        """ Get either LEGACY or TI based on the given file size. """
        return next((t for t in cls if t.value.matches_size(size)), None)


def read_until(fp: BinaryIO, c: bytes):
    """ Read from the binary stream until the given character is encountered. """
    buf = b''
    while (match := fp.read(1)) != c:
        buf += match
    return buf


def get_dsp_bank_data(fp: BinaryIO, model_type: AccessVirusType) -> DSPBankData:
    """
    Retrieve the dsp related data from the flash memory banks.
    """
    data = []
    idx = 0xff
    offset = model_type.value.dsp_offset
    while idx > 0:
        logger.debug("Seeking to 0x%x", offset)
        fp.seek(offset)

        idx = int.from_bytes(fp.read(1), 'big')
        size1 = int.from_bytes(fp.read(1), 'big')
        size2 = int.from_bytes(fp.read(1), 'big')
        word_count = (size1 - 1) << 8 | size2

        logger.debug("Index: %d, size=0x%x", idx, word_count)
        for i in range(word_count):
            data.append(int.from_bytes(fp.read(3), 'big'))

        offset += 0x8000

    # Read version
    version = read_until(fp, b'\xFF').decode('ascii')
    logger.debug("Version: %s", version)

    return DSPBankData(version, data)


def get_dsp_chunk_data(bank_data: DSPBankData) -> DSPChunkData:
    """
    Parse the BootROM and command stream from the dsp bank data.
    """
    bootrom_size = bank_data.data[0]
    bootrom_offset = bank_data.data[1]
    bootrom_data = bank_data.data[2:2+bootrom_size]
    chunk_data = bank_data.data[2+bootrom_size:]
    assert len(bootrom_data) == bootrom_size

    return DSPChunkData(bootrom_size, bootrom_offset, bootrom_data, chunk_data)


def get_dsp_commands(chunk_data: List[int]) -> List[DSPCommandData]:
    """
    Parse the command stream into individual command entries.
    """
    commands = []
    idx = 0
    while idx < len(chunk_data):
        cmd = chunk_data[idx]
        addr = chunk_data[idx+1]
        size = next(iter(chunk_data[idx+2:idx+3]), 0)  # size can be empty for cmd = 4
        data = chunk_data[idx+3:idx+3+size]
        logger.info("Command %d, addr=0x%06x, size=0x%06x", cmd, addr, size)
        commands.append(DSPCommandData(cmd, addr, size, data))
        idx += 3 + size

    return commands
