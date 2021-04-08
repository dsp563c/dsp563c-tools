; Motorola DSP56303 Access Virus A [v280g]
device dv00 56303

;;; Load BootROM and CommandStream via HDI08
input x:$FFFFC3 .\bits_high_repeat.io
input x:$FFFFC6 .\output\virus_a_v280g.bootrom_command_stream.patched.be.io

;;; Make audio available
input x:$FFFFB7  .\bits_toggle.io

;;; Put simulator into i8051 mode
reset D m1          ; Use $ffff00 as entrypoint
change omr $30e     ; Enable DMA and HDI08 bootstrap

;;; Enable logging
;log S session.log -O

;;; BootROM breakpoints
break p:$100        ; bootrom entrypoint
;break p:$2543e      ; bootrom command handler

;; Program breakpoints
break p:$0          ; in case something goes wrong (nullptr jmp)
break p:$9a6        ; main entrypoint
break p:$2c184      ; audio ready
break p:$2c186      ; setup
break p:$2c189      ; main loop

go
