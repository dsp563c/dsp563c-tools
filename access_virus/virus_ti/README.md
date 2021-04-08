# VirusTI Install Extraction Tool

This tool will help extract files from the Access Virus TI 
installation media.

You will end up with at least two ROM files:

 * F.bin: contains the flash dump for the Access Virus TI EEPROM
 * P.bin: contains preset data

## Requirements

 * python3
 
## Extracting firmware files

Extract all the files from `firmware_bin64` to `./output64/` folder:

```bash
$ python3 firmware.py firmware_bin64 output64
INFO:__main__:Opening firmware file firmware_bin64
INFO:__main__:Writing entry lcd_backup_000.bin
... (omitted for brevity)
INFO:__main__:Writing entry vti.bin
INFO:__main__:Writing entry vti_2.bin
INFO:__main__:Writing entry vti_snow.bin
INFO:__main__:Writing entry Changes.htm
INFO:__main__:Writing entry Welcome.htm
INFO:__main__:Writing entry BTN_Help.png
INFO:__main__:Writing entry KemperAmps-Banner.png
INFO:__main__:Writing entry KemperAmps-Head.png
INFO:__main__:Writing entry vcstyles.css
INFO:__main__:Successfully wrote chunks to folder output64
```

## Extracting VTI binary files

```bash
$ python3 vti.py output64/vti.bin output64_vti/
INFO:__main__:Opening vti file output64/vti.bin
INFO:__main__:Successfully wrote ROM to output64_vti//F.bin
INFO:__main__:Successfully wrote ROM to output64_vti//P.bin
```

## Known issues

The vti_2.bin file seems to use a different format for P.bin.
This will result in an error when running `vti.py`.
See the code for more details.

Extraction of F.bin and S.bin will still work. 
