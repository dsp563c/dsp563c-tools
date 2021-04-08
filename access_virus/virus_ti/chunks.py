from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class InstallChunk:
    name: str
    size: int
    data: bytes


def get_chunks(fp):
    """ Helper function to deal with the install chunk format. """
    chunks = []
    file_id = fp.read(4).decode()
    file_size = int.from_bytes(fp.read(4), 'big')
    logger.debug('Reading %s, size=0x%x', file_id, file_size)

    while fp.tell() < file_size:
        chunk_id = fp.read(4).decode()
        chunk_size = int.from_bytes(fp.read(4), 'big')
        data = fp.read(chunk_size)
        logger.debug("Chunk %s, size=0x%x", chunk_id, chunk_size)
        chunks.append(InstallChunk(name=chunk_id, size=chunk_size, data=data))

    return chunks
