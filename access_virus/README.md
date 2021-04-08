# Access Virus Tools

This document will show how to extract DSP memory regions from a flash
memory dump of any Access Virus model (both legacy and TI models
are supported).

It will also provide some guidelines on how to run the firmware in the
Motorola Simulator.

An additional extraction tool necessary for Access Virus TI can be found
in the `virus_ti` directory.
 
## Extracting BootROM and CommandStream

The CommandStream contains the binary data we need to extract the DSP code.

Use the `dump_bootstrap.py` script to extract both the BootROM and the 
CommandStream:

```bash
$ python3 dump_bootstrap.py
INFO:__main__:Usage: python3 dump_bootstrap.py <flash_file> <output_file_prefix>
```

Example for Access Virus C:

```bash
$ python3 dump_bootstrap.py access_virus/virus_c/vc_650g/access_virus_c_am29f040b_6v6.bin dsp
INFO:__main__:Flash version: (C)ACCESS [12-14-2009-18:22:54][vc_650g], Size: 0xb8d4
INFO:__main__:BootROM size: 0x51
INFO:__main__:BootROM offset: 0x100
INFO:__main__:CommandStream size: 0xb881
INFO:__main__:Successfully wrote BootROM to dsp.bootrom.be.bin
INFO:__main__:Successfully wrote BootROMStream to dsp.bootrom_stream.be.bin
INFO:__main__:Successfully wrote CommandStream to dsp.command_stream.be.bin
```

Example for Access Virus TI:

```bash
$ python3 dump_bootstrap.py access_virus/virus_ti/51700/roms/vti_2/F.bin virus_ti_2
INFO:__main__:Flash version: wvd119.lod 08/05/12-15:34:15 (C)ACCESS MUSIC, Size: 0x27d62
INFO:__main__:BootROM size: 0x47
INFO:__main__:BootROM offset: 0x100
INFO:__main__:CommandStream size: 0x27d19
INFO:__main__:Successfully wrote BootROM to virus_ti_2.bootrom.be.bin
INFO:__main__:Successfully wrote BootROMStream to virus_ti_2.bootrom_stream.be.bin
INFO:__main__:Successfully wrote CommandStream to virus_ti_2.command_stream.be.bin
```

## Extracting the DSP memory regions

Once we have the command stream, we could start the simulator and have
BootROM prepare the memory sections. But we also provide a tool that mimics
this behavior and allows you to extract the P, X and Y memory regions.

```bash
$ python3 dump_dsp_memory.py
INFO:__main__:Usage: python3 dump_dsp_memory.py <cmd_stream_file> <output_file_prefix>
```

Example for Access Virus C:

```bash
$ python3 dump_dsp_memory.py dsp.command_stream.be.bin dsp_memory
...
INFO:__main__:Discovered entrypoint (command = 4) @ 0xda6
INFO:__main__:Writing region p to dsp_memory.p.be.bin
INFO:__main__:Writing region x to dsp_memory.x.be.bin
INFO:__main__:Writing region y to dsp_memory.y.be.bin
```

Remember to use our tool `be2le.py` in the `dsp56k` directory to convert
it to little endian so that you can load it up into IDA Pro.

## Running in the Motorola DSP Simulator

We can perform static binary analysis on the code we extracted earlier,
but we can also try to run the device into the Motorola Simulator,
to get even more insight in how it works.

Check out the simulator documentation `DSPS56SIMUM.pdf` for details
on how to use it (included in the Chameleon SDK).

### Macros

We recommend to create macro files to setup the simulator. 
Macros are text files that contain the commands that are
provided to the simulator. They can be used to define
breakpoints or other setup instructions.

You can use a macro as follows:
```
.\sim56300.exe macro.cmd
```

We'll be showing some example macros below.

### Peripherals

The DSP will communicate with external chips via special memory
addresses that you can simulate as follows:
`input x:$<addr> local_file.io`

The `local_file.io` can contain a series of values that will 
be provided each time the DSP reads a value from `<addr>`.

Use the tool `bin2io.py` to create such an IO file for data
such as the CommandStream.

### Byte-patching

When running code in the simulator, you will run into several
issues due to changes to the OMR and SR registers. These are
special register types that influence specific behavior of the
DSP. During our tests, we had to patch these instructions to
disable some bits such as Instruction Cache and Address Priority
Disable (APD).

Another tool `patch_omr_sr.py` is provided to take care of this.

### Shared memory space

We ran into an issue where a pointer was being access from Y memory,
but this memory did not contain a valid pointer. Jumping to
this nullpointer results in a crash. We found out that in X memory,
there *was* a valid pointer at the given memory location. 
This probably has something to do with memory regions that are shared
between X and Y (and possibly P). Could have something to do with how
the AAR registers are configured, but we havent been able to figure it
out yet.

The way we addressed this issue is by duplicating some X memory to Y
memory space by duplicating the last entry of the CommandStream and
changing the cmd (01) to (02) so that this data will be copied to both
X and Y memory.

### Approach 1: Motorola DSP56362 (SHI Bootstrapped)

The simulator comes with a device type 56362 that we will use to load up
the Virus C. This device has a built-in bootstrap program that will read
the BootROM from a specific peripheral based on the operating mode.

We will use the SHI interface which is part of mode 7.

Byte-patch the instructions that set the OMR and SR registers:

```
./dsp56k/patch_omr_sr.py dsp.bootrom_stream.be.bin dsp.bootrom_stream.patched.be.bin
./dsp56k/patch_omr_sr.py dsp.command_stream.be.bin dsp.command_stream.patched.be.bin
```  
This will change the following instructions

 * `05f43a 004080` -> `05f43a 000080` (disable APD)
 * `05f439 080000` -> `05f439 000000` (disable IC)

Create a `bits_high_repeat.io` file:
```
($FFFFFF)
```

Create a `bits_toggle.io` file:
```
(FFFFFF#2 000000#2)
```

Create the BootROM IO file:
```
./dsp56k/bin2io.py dsp.bootrom_stream.patched.be.bin dsp.bootrom_stream.patched.be.io
```

Create the CommandStream IO file (repeat values twice):
```
./dsp56k/bin2io.py dsp.command_stream.patched.be.bin dsp.command_stream_repeat.patched.be.io 2
```

Run the following macro:
```
; Motorola DSP56362 Access Virus C [vc_650g]
device dv00 56362

;;; Load BootROM via SHI
input x:$FFFF91 bits_high_repeat.io
input x:$FFFF94 .\output\virus_c_vc_650g.bootrom_stream.patched.be.io

;;; Load CommandStream via HDI08
input x:$FFFFC3 .\bits_high_repeat.io
input x:$FFFFC6 .\output\virus_c_vc_650g.command_stream.patched.be.io

;;; Make ESAI available
input x:$FFFFB3 bits_toggle.io

;;; Set operation mode to load from SHI
reset D m7

;;; Breakpoints
break p:$100        ; BootROM entrypoint
;break p:$30024      ; Process new command
break p:$da6        ; DSP entrypoint

go

```

The simulator will go through the following phases:
1. Runs built-in bootstrap program @ 0xFF0000
2. Loads BootROM from SHI and writes to specified offset (0x100)
3. Jumps to BootROM at offset 0x100
4. BootROM will copy itself to offset 0x30000 and jumps there
5. Loads CommandStream via Host interface and prepares P, X and Y RAM
6. Jumps to DSP entrypoint at offset 0xda6


### Approach 2: Motorola DSP56303 (HDI08 Bootstrapped, i8051 mode)

After we got the first example working, we noticed some ROMs are using the
SHI interface to receive data. Because we already mapped SHI IO to the 
`dsp.bootrom_stream.io`, we might run into some conflicts here. 
We could turn off the I/O after the BootROM finished, but instead we 
tried to load both the BootROM and the CommandStream via HDI08 (this is
also how the original hardware does it).

We got it to work by tricking the Simulator in a reserved mode and preparing
the IO file in the right way.

Prepare both the BootROM and CommandStream in the same way as Example 1, and
concatenate the two files:
`cat dsp.bootrom_stream.patched.be.io dsp.command_stream_repeat.patched.be.io >> dsp.bootrom_command_stream.patched.be.io`

Use the following macro:
```
; Motorola DSP56303 Access Virus A [v280g]
device dv00 56303

;;; Load BootROM and CommandStream via HDI08
input x:$FFFFC3 .\bits_high_repeat.io
input x:$FFFFC6 .\output\dsp.bootrom_command_stream.patched.be.io

;;; Make audio available
input x:$FFFFB7  .\bits_toggle.io

;;; Put simulator into i8051 mode
reset D m1          ; Use $ffff00 as entrypoint
change omr $30e     ; Enable DMA and HDI08 bootstrap

;;; Breakpoints
break p:$100        ; bootrom entrypoint
;break p:$2543e      ; bootrom command handler
break p:$9a6        ; main entrypoint

go

```

### Approach 3: Motorola DSP56362 (NON-Bootstrapped, OMF/LOD loading)

We also tried creating an LOD file using the tool `be2lod.py` (combining
P, X and Y) and loading that directly into the Simulator, basically bypassing
the entire BootROM procedure, but we kept running into crashes and couldn't 
get it working properly.


### Troubleshooting

#### Simulator steps half in between instructions

Did you correctly patch the OMR/SR instructions?
Disabling the Instruction Cache in the SR register should fix this.

#### During simulation the process jmps to p:$0

This is probably caused by missing data in Y memory space.
It appears memory from X is shared with Y. During runtime,
the process accesses pointers from Y memory where it jumps to.
If these memory regions are empty, a jmp to p:$0 occurs.

We fixed this by duplicated the one before last command (cmd=1)
and changing cmd to 2 so that it also writes these values to
Y memory.

#### Simulator crashes when writing to P memory

Make sure the Memory Switch Mode bit in the OMR is enabled.
We found that without this bit, writing to the lower region
of P memory results in a crash.

You can try if this helps in the Simulator with this command:
```
change omr $80
```

#### Illegal instruction encountered: pflush

Did you correctly patch the OMR instructions?
Disabling the ADP in the OMR register should fix this.
