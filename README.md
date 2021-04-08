# DSP563 Community Tools

This repository contains technical documentation and a set of tools that 
facilitate research of various virtual analog synthesizers.

## Access Virus

All technical information we discovered on the architecture of 
the Access Virus synthesizer series is documented here.

See the `access_virus` directory for a guide on how to use the tools
and for additional information on specific hardware versions.

### Hardware versions
 
* 1997 Virus A - 1 x Motorola DSP 56303, 1x SAB 80C535-N
* 1999 Virus B - 1 x Motorola DSP 56311, 1x SAB 80C535-N
* 2002 Virus C - 1 x Freescale DSP 56362, 1x SAF 80C515-L24N
* 2005 Virus TI - 2 x Freescale DSP 56367 - 2x150 MHz, 1x ST UPSD3212CV
* 2009 Virus TI2 - 2 x Freescale DSP 56321 - 2x275 MHz

### Motorola DSP563xx

Each synthesizer has at least one 24-bit DSP (Motorola DSP563xx series)
that performs the audio processing. Detailed information on the
device and instruction set can be found in the corresponding Motorola 
User Manual and DSP56300 Family Manual.

### i8051 microcontroller

Handling user inputs from knobs and showing data on an LED display is 
handled by an 8-bit MCU with the Intel i8051 instruction set.
This microcontroller also takes care of initializing the DSP. The DSP
is connected to the microcontroller via the Host Interface (HDI08).
  
### Flash memory 

The flash memory contains all the code and data the synthesizer needs to 
operate. All legacy models have 512K flash memory, the newer TI and TI2
models feature a total of 1M.

#### Contents
 * i8051 operating system
 * i8051 flash programming routines
 * DSP563xx code (PRAM) and memory (XRAM, YRAM)
 * Presets and other data
 
#### Layout

Flash memory is split up in banks of 32K (`0x8000`) bytes. This allows the 
memory to be directly addressable by the microcontroller, because the i8051
microcontroller only has 16 bits of address space for XRAM (`0x0 - 0xFFFF`).

The lower half of this address space (`0x0 - 0x8000`) always points to the 
first bank of the flash memory, while the upper half (`0x8000 - 0xFFFF`),
can point to any other bank of the flash memory. This is achieved by a 
bank switching routine of the microcontroller.

The bank switching routine accepts one argument A, which can be mapped to 
a file offset in flash using: `offset = (A & 0xF0) << 11`. The low nibble 
is ignored. Note that we only verified this on legacy virus models (with 
512K flash).

Example for `A = 0x10`: `(0x10 & 0xF0) << 11 == 0x8000`

#### Banks

The exact structure of the banks differs from synthesizer model to model,
but for 512K flash it roughly looks like this:

```
[ bank 0 - 2  ] i8051 operating system code
[ bank 3 - 7  ] DSP563xx BootROM + chunks
[ bank 7      ] i8051 flash programming routines 
[ bank 8 - 15 ] preset data
```

### Execution flow

The i8051 microcontroller will go through the following initialization phases:

1. Flash memory is bank switched into the i8051 program address space.
2. i8051 execution starts at 0x0, which is an `ljmp RESET_0`.
3. RESET_0 routine will:
    * Perform generic initialization routines
    * Start DSP initialization (see below)
    * ... (TODO)
    
### DSP initialization

The microcontroller will initialize the DSP by reading 24bit words from
several banks in flash. For legacy models, the DSP data starts at bank 3
(offset 0x18000). For TI and TI2, the DSP data starts at bank 14
(offset 0x70000).

#### Bank parsing

Each bank is structured like this:

`
[ 1 byte index ] [ 1 byte size1 ] [ 1 byte size2 ]  [ 3 byte words ... ]
`

The number of words to be read can be calculated as follows:
`word_count = (size1 - 1) << 8 | size2`

With each bank read, the index will decrement. The last bank to be read
has an index of 0. At the end of the last bank there is a string terminated
with a null-byte that represents the version of the firmware.

#### Bank data stream
The resulting data stream is structured like this (each element is one word
/ 24bits):

`
[ bootrom_size ] [ bootrom_offset ] 
[ bootrom_data ... ] [ chunk_data ... ]
`

This datastream is sent over the HDI08 port which is connected to the DSP.
The built-in bootstrap program of the DSP running at `0xffff00` will read
`bootrom_size` words and writes them to PRAM memory at offset `bootrom_offset`.
(usually `0x100`). Execution will start there and the BootROM
will be retrieving the remaining `chunk_data` from the same HDI08 port.

The assembly source code of the built-in bootstrap program can be found in 
Appendix A of the Motorola User Manual.

#### DSP chunk data

The BootROM can be disassembled to see exactly how it processes the remaining
chunk data, but the process is briefly described here.

Chunk structure: `[ cmd ] [ addr ] [ size ] [ words ... ] `

The `size` element indicates the number of words in the chunk.

The `addr` element indicates the destination address for the words.

##### Commands
```
000000: Write to P memory
000001: Write to X memory
000002: Write to Y memory
000003: Write to Y memory (split up each word in two 12-bit values)
000004: Jump to address (start execution)
```

### Reverse engineering
Both the microcontroller code and the DSP code can be disassembled using
your favourite disassembler (we are using IDA Pro).

#### Microcontroller
Just load the entire flash rom into IDA and select Intel 8051 as the processor
type (and select the correct device name, see the hardware list).
The RESET_0 routine should be visible (which is the main entrypoint).

Note that some routines are not recognized automatically (such as the
flash programming ones). You can go to the correct offset and press `c`
to instruct IDA to disassemble those.

### DSP code
You can use the tools in this repository to extract the DSP program
from any Access Virus flash dump file.

It performs the BootROM method described above to extract the DSP memory and
write it to a file. Then load up IDA and select dsp563xx as the processor type.

The entrypoint can be determined by looking at command 4.

We stumbled upon an issue with the cross-references in IDA. With the `jclr` 
instruction for example, IDA seems to ignore the high bits of the destination
address, causing a wrongly displayed x-ref. Unfortunately, we did not yet 
find a good solution to this problem.

Some helpful scripts and configuration files are available in the `ida` 
directory.

Keep in mind that IDA Pro loads dsp563xx binaries using little endian, while
the DSP563 itself uses big endian byte order (we included a tool be2le.py to
make conversion easy :) 

## Contributing

Feel free to join us on [Discord](https://discord.gg/x6epkzvHXx) if you'd like to help out! 

### External Resources

* https://github.com/mamedev/mame/blob/master/src/mame/drivers/acvirus.cpp
* https://adriangin.wordpress.com/2018/09/27/virus-ti-hardware-firmware/
* https://www.chameleon.synth.net/
