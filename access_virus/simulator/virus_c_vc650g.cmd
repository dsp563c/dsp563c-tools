; Motorola DSP56362 Access Virus C [vc_650g]
device dv00 56362

;;; Load BootROM via SHI
input x:$FFFF91 bits_high_repeat.io
input x:$FFFF94 .\output\virus_c_vc_650g.bootrom_stream.patched.be.io

;;; Load CommandStream via HDI08
input x:$FFFFC3 .\bits_high_repeat.io
input x:$FFFFC6 .\output\virus_c_vc_650g.command_stream.patched.be.io

;;; Make audio available
input x:$FFFFB3 bits_toggle.io

;;; Set operation mode to load from SHI
reset D m7

;;; BootROM breakpoints
break p:$100        ; BootROM entrypoint
;break p:$30024      ; Process new command
break p:$da6        ; DSP entrypoint


go
