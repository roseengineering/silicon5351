
# silicon5351

A MicroPython and CircuitPython library for controlling the SI5351 chip.
The library also supports generating quadrature output
using the phase offset feature of the chip.

# Introduction

The file silicon5351.py contains the actual si5351 library. This library 
provides the SI5351\_I2C class to control the Silicon Labs SI5351x range of chips.

This class also supports quadrature output.  The lowest frequency which 
can be outputted in quadrature is limited by the chip hardware 
to clock's PLL frequency divided by 128.

## Example

```python
from silicon5351 import SI5351_I2C

import sys
if sys.implementation.name == 'circuitpython':
    import board, busio
    # i2c = busio.I2C(board.SCL, board.SDA) # XIAO RP2040
    i2c = busio.I2C(board.GP5, board.GP4)   # PICO
    while not i2c.try_lock():
        pass
else:
    import machine
    i2c = machine.I2C(1, scl=machine.Pin(7), sda=machine.Pin(6))

crystal = 25e6     # crystal frequency
mult = 15          # 15 * 25e6 = 375 MHz PLL frequency
freq = 3.0e6       # output frequency with an upper limit 200MHz
quadrature = True  # lower limit for quadrature is 375MHz / 128
invert = False     # invert option ignored when quadrature is true

si = SI5351_I2C(i2c, crystal=crystal)
si.setup_pll(pll=0, mult=mult)
si.init_clock(output=0, pll=0)
si.init_clock(output=1, pll=0, quadrature=quadrature, invert=invert)
si.set_freq_fixedpll(output=0, freq=freq) 
si.set_freq_fixedpll(output=1, freq=freq) 
si.enable_output(output=0)
si.enable_output(output=1)
print(f'done freq={freq} mult={mult} quadrature={quadrature} invert={invert}')
```

The library calls the PLL soft reset function 
of the chip whenever the MultiSynth whole number portion
of the divisor changes or is intitialized.
This soft reset is required in order to generate a quadrature
or an inverted output.  It is also required to synchronize all outputs 
derived off a particular PLL, in order for them to be coherrent.

## API

<code>class silicon5351.<b>SI5351\_I2C</b>(self, i2c, crystal, load=3, address=96)</code>  
Instantiate the SI5353\_I2C class.  All clock outputs
(clkouts) will be shutdown and disabled.  
**i2c** The MicroPython or CircuitPython I2C object.  
**crystal** The crystal frequency in Hz.  
**load** The load capacitance of crystal.  Must use one of         the global constants defined in the library for this value.  
**address** The I2C address of the si5351 chip.  

Instances of the <code>silicon5351.<b>SI5351\_I2C</b></code> class have the following public properties and methods:   

<code>SI5351\_I2C.<b>init\_clock</b>(self, output, pll, quadrature=False, invert=False, integer\_mode=False, drive\_strength=3)</code>  
Initialize the given clock output (clkout).
This method must be called before using set\_freq\_fixedpll() on
the output.  
**output** The number of the clock output (clkout) to initialize   
**pll** The number of the PLL to select. (0=PLLA, 1=PLLB)  
**invert** Invert the output.  
**quadrature** Invert the output and also enable quadrature         logic in the library.  
**integer\_mode** Enable enable integer mode for this output.  
**drive\_strength** The drive strength in current to use         for the output. Must use one of the global constants defined         in the library for this value.  

<code>SI5351\_I2C.<b>enable\_output</b>(self, output)</code>  
Enable the given clock output (clkout).  
**output** The clock output (clkout) to enable.  

<code>SI5351\_I2C.<b>disable\_output</b>(self, output)</code>  
Disable the given clock output (clkout).  
**output** The clock output (clkout) to disable.  

<code>SI5351\_I2C.<b>disabled\_states</b>(s0=0, s1=0, s2=0, s3=0, s4=0, s5=0, s6=0, s7=0)</code>  
Set the state of the clock outputs (clkout) when one
or more clocks are disabled either in software or
as a result of the output enable (OEB) pin going active.
The possible disabled states for an output are low voltage, high
voltage, high impedance, and never disabled.  
**s0..s7** The disabled state to set for the appropriate clock         output (clkout).  Must use one of the global constants defined in         the library for this value.  

<code>SI5351\_I2C.<b>disable\_oeb</b>(self, mask)</code>  
Disable the output enable (OEB) pin for the given
clock outputs (clkouts).  
**mask** A bit mask of the clock outputs (clkouts) to disable         output enable (OEB) pin support for.  

<code>SI5351\_I2C.<b>setup\_pll</b>(self, pll, mult, num=0, denom=1)</code>  
Set the frequency for the given PLL.
The PLL frequency is set to the frequency given by
(mult + num / denom) times the crystal frequency.  
**pll** The number of the PLL to select. (0=PLLA, 1=PLLB)  
**mult** The whole number to multiply the crystal frequency         by.  This value must be in the range [15-90].  
**num** The numerator to multiply the crystal frequency         by. This value must be in the range [0-1048575).  
**denom** The denominator to multiply the crystal         frequency by. This value must be in the range (0-1048575].  

<code>SI5351\_I2C.<b>set\_freq\_fixedpll</b>(self, output, freq)</code>  
Set the frequency for the clock output (clkout).  Must
call init\_clock() and setup\_pll() before calling this method.  
**output** The number of the clock output (clkout) to         set the frequency for.  
**freq** The frequency in Hz to set the clock output (clkout) to.  


