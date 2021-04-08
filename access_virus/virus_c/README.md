# Access Virus C Analysis [vc_650g]

## Peripheral and operation configuration
| Addr       | Direction | Bit | Value | Description  | Usage        |
|------------|-----------|-----|-------|--------------|--------------|
| `0xfffff5` | Read      | 0   | 1     | Debugging    | Enable debug |

### Configure Operation Mode Register (OMR) & Status Register (SR)
```
ROM:0105                  movec   #$4080,omr   ; BootROM
ROM:0107                  movec   #$80000,sr
..
ROM:0DB2                  movec   #$4380,omr   ; Default OMR
ROM:0DB4                  movec   #$80000,sr
...
ROM:2C3F9                 movec   #$4080,omr   ; turns of Core-DMA (not sure when)
ROM:2C3FB                 movec   #$80000,sr
...
ROM:2C46C                 movec   #$438E,omr   ; before reset and jmps to boot program

>>> '{:b}'.format(0x4380)          # Default OMR
'1000011 10000000'
  bit 7:  MS   => Memory Switch Mode
  bit 8:  CPD0 => Core-DMA Priority 0
  bit 9:  CPD1 => Core-DMA Priority 1
  bit 14: Address Priority Disable 

>>> '{:b}'.format(0x438E)          # OMR during boot program
'1000011 10001110'
  bit 1:  MB  \
  bit 2:  MC   => HDI08 Bootstrap in 8051 multiplexed bus mode
  bit 3:  MD  /
  bit 7:  MS   => Memory Switch Mode
  bit 8:  CPD0 => Core-DMA Priority 0
  bit 9:  CPD1 => Core-DMA Priority 1
  bit 14: APD  => Address Priority Disable

Status register bit == instruction cache

```

### Configure Address Attribute Registers

```
ROM:0109                 movep   #$20739,x:<<AAR0   ; In BootROM
ROM:010B                 movep   #$30839,x:<<AAR1
...
ROM:0DB6                 move    #1,x0              ; Entrypoint
ROM:0DB8                 movep   #$539,x:<<AAR0
ROM:0DBA                 movep   #$30839,x:<<AAR1
ROM:0DBC                 movep   x0,x:<<AAR2
ROM:0DBD                 movep   x0,x:<<AAR3

>>> '{:b}'.format(0x20739)    # AAR0 in BootROM
'10 00000111 00111001'
  bit 0:  BAT0  => Bus Access Type == SRAM
  bit 3:  BPEN  => Bus Program Memory Enable
  bit 4:  BXEN  => Bus X Data Memory Enable
  bit 5:  BYEN  => Bus Y Data Memory Enable
  bit 8:  BNC0 
  bit 9:  BNC1
  bit 10: BNC2
  bit 17: BAC5

>>> '{:b}'.format(0x30839)   # AAR1 in BootROM
'11 00001000 00111001'
  bit 0:  BAT0  => Bus Access Type == SRAM
  bit 3:  BPEN  => Bus Program Memory Enable
  bit 4:  BXEN  => Bus X Data Memory Enable
  bit 5:  BYEN  => Bus Y Data Memory Enable
  bit 11: BNC3
  bit 16: BAC4
  bit 17: BAC5

>>> '{:b}'.format(0x539)    # AAR0 in Entrypoint
'101 00111001'
  bit 0:  BAT0  => Bus Access Type == SRAM
  bit 3:  BPEN  => Bus Program Memory Enable
  bit 4:  BXEN  => Bus X Data Memory Enable
  bit 5:  BYEN  => Bus Y Data Memory Enable
  bit 8:  BNC0
  bit 10: BNC2
```

### Configure Bus Control
```
ROM:0DAB                 movep   #$12421,x:<<BCR

>>> '{:b}'.format(0x12421)
'1 00100100 00100001'
  bit 0:  BA0W0
  bit 5:  BA1W0
  bit 10: BA2W0
  bit 13: BA3W0
  bit 16: BDFW0
```

### Configure Interrupt Priority
```
ROM:0DAD                  movep   #$E07,x:<<$FFFFFF
...
ROM:2C1BC                 movep   #$555000,x:<<$FFFFFF  ; IRQ is disabled here?
ROM:2C1BE                 movep   #$35B,x:<<$FFFFFE

>>> '{:b}'.format(0xe07)
'1110 00000111'
  bit 0:  IAL0  = IRQA Priority 2
  bit 1:  IAL1  
  bit 2:  IAL2  = IRQA Trigger Mode: Neg. Edge
  bit 9:  IDL0  = IRQD Priority 2
  bit 10: IDL1
  bit 11: IDL2  = IRQD Trigger Mode: Neg. Edge

>>> '{:b}'.format(0x555000)
'1010101 01010000 00000000'
  bit 12: D0L0  = DMA0 Priority 0
  bit 14: D1L0  = DMA1 Priority 0
  bit 16: D2L0  = DMA2 Priority 0
  bit 18: D3L0  = DMA3 Priority 0
  bit 20: D4L0  = DMA4 Priority 0
  bit 22: D5L0  = DMA5 Priority 0

>>> '{:b}'.format(0x35b)
'11 01011011'
  bit 0:  ESL0  = ESAI  Priority 2
  bit 1:  ESL1
  bit 3:  SHL1  = SHI   Priority 1
  bit 4:  HDL0  = HDI08 Priority 0
  bit 6:  DAL0  = DAX   Priority 0
  bit 8:  TAL0  = TEC   Priority 2
  bit 9:  TAL1
```

### Configure HDI08 (Host Port) 
Connection to: SAF i8051 microcontroller.
```
ROM:280E3                 movep   #$1C1E,x:<<HDI08__HPCR ; configure M_HPCR as I8051HOSTLD

>>> '{:b}'.format(0x1C1E)
'11100 00011110'  => I8051HOSTLD
```

### Configure SHI (Serial Host Interface)

Connection to: Unknown
```
ROM:2BFD5                 movep   #$183,x:<<SHI__HCKR
ROM:2BFD7                 movep   #$41,x:<<SHI__HCSR
...
ROM:2BFE6                 movep   #$181,x:<<SHI__HCKR

>>> '{:b}'.format(0x183)     # HCKR, SHI Clock Control Register
'1 10000011'
  bit 0: CPOL, Clock Polarity
  bit 1: CPHA, Clock Phase
  bit 7: HCKR Divider Modulus Select
  bit 8: HCKR Divider Modulus Select

>>> '{:09b}'.format(0x41)    # HCSR, SHI Control/Status Register
'0 01000001'
  bit 0: HCSR Host Enable
  bit 6: HCSR Master Mode

```

### Configure ESAI Receive
Connection to: Digital to Analog Converter
```
ROM:2C1C8                 movep   #$40200,x:<<$FFFFB8  # ESAI RECEIVE CLOCK CONTROL REGISTER (RCCR)
ROM:2C1CA                 movep   #$7D00,x:<<$FFFFB7   # ESAI RECEIVE CONTROL REGISTER (RCR)
...
ROM:2C1D9                 bset    #0,x:<<$FFFFB7

'{:b}'.format(0x40201)      # RCCR
'100 00000010 00000001'
  bit 1:  RPM0    -> prescale divider = 2
  bit 9:  RDC0 Rx -> frame rate divider = 2
  bit 18: RCKP    -> polarity

>>> '{:b}'.format(0x7D00)   # RCR
'1111101 00000000'
  bit 8:  RMOD0 -> Network Mode (RDC{0:4} == 0x1)
  bit 10: RSWS0 \
  bit 11: RSWS1  \
  bit 12: RSWS2   => Slot length: 32, Word length: 24 
  bit 13: RSWS3  /
  bit 14: RSWS4 /
```

### Configure ESAI Transmit
Connection to: Digital to Analog Converter
```
ROM:2C1C4                 movep   #$440200,x:<<ESAI__TCCR
ROM:2C1C6                 movep   #$D07D00,x:<<ESAI__TCR
ROM:2C1D8                 bset    #0,x:<<ESAI__TCR
...
ROM:2C204                 bset    #23,x:<<ESAI__TCR
...
ROM:2C238                 bset    #1,x:<<ESAI__TCR  ; after ESSI0TxdwExcept transmit
ROM:2C239                 bset    #2,x:<<ESAI__TCR

>>> '{:b}'.format(0x440200)
'1000100 00000010 00000000'
  bit 9:  TDC0 Tx -> frame rate divider = 2
  bit 18: TCKP    -> polarity 
  bit 22: TFSD    -> FST as output

>>> '{:b}'.format(0xD07D07)
'11010000 01111101 00000111'
  bit 0:  TE0
  bit 1:  TE1
  bit 2:  TE2
  bit 8:  TMOD0 => Network Mode (TDC{0-4} == 0x1)
  bit 10: TSWS0 \
  bit 11: TSWS1  \
  bit 12: TSWS2   => Slot length: 32, Word length: 24
  bit 13: TSWS3  /
  bit 14: TSWS4 /
  bit 20: TEIE => Transmit Exception Interrupt Enable
  bit 22: TIE  => Transmit Interrupt Enable
  bit 23: TLIE => Transmit Last Slot Interrupt Enable
```

### Configure ESAI Status
Connection to: Digital to Analog Converter
```
ROM:0DC0                  bclr    #14,x:<<ESAI__SAISR  ; in ESSIO Tx interrupt handler
...
ROM:2C1CC                 movep   #0,x:<<ESAI__SAICR
...
ROM:2C207                 jclr    #13,x:<<ESAI__SAISR,ROM_C207
ROM:2C209                 jset    #13,x:<<ESAI__SAISR,ROM_C209

bit 13: TFS  => SAISR Transmit Frame Sync Flag
bit 14: TUE  => SAISR Transmit Underrun Error Flag
```

### Configure Port C
According to DSP56362.pdf, Port C is used for ESAI. 
```
ROM:00F1                  bset    #2,x:<<PORTC__PRRC
ROM:00F2                  bclr    #2,x:<<PORTC__PDRC
...
ROM:2C1CE                 movep   #$E5B,x:<<PORTC__PRRC
ROM:2C1D0                 movep   #$85B,x:<<PORTC__PCRC
ROM:2C1DA                 bset    #7,x:<<PORTC__PRRC
ROM:2C1DB                 bset    #7,x:<<PORTC__PDRC
ROM:2C1DC                 bset    #2,x:<<PORTC__PRRC
ROM:2C1DD                 bclr    #2,x:<<PORTC__PDRC
...
ROM:2C23A                 bset    #9,x:<<PORTC__PCRC   ; after ESSI0TxdwExcept transmit
ROM:2C23B                 bset    #10,x:<<PORTC__PCRC
```

### Configure Port D
According to DSP56362.pdf, Port C is used for DAX.
```
ROM:0163                  bclr    #0,x:PORTD__PDRD
...
ROM:0166                  bset    #0,x:PORTD__PDRD
...
ROM:2C1DE                 movep   #3,x:<<PORTD__PRRD
ROM:2C1E0                 movep   #3,x:<<PORTD__PDRD
```


### Configure Timers
TODO


## Connected Pins
### SHI
```
i2c                            SPI
* HA0  ->  33  [connected]     MOSI -> 143    --
* HA2  ->  31  --              SS   ->   2    --   
* SDA  -> 144  [connected]     MISO -> 144    [connected]
* SCL  ->   1  [connected]     SCK  ->   1    [connected]
* HREQ ->   3  --              HREQ ->   3    --
```

### JTAG / OnCE
```
* TCK   -> 141  [ connected ]  Test Clock
* TDI   -> 140  [ connected ]  Test Data In
* TDO   -> 139  [ -- ]         Test Data Out
* TMS   -> 142  [ -- ]         Test Mode Select
* TRST  -> 138  [ connected ]  Test Reset (Optional)
* DE    -> 53   [ connected ]  Debug Event (In/Out)  ! not 5v tolerant !
```