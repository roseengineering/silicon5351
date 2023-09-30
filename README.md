
# silicon5351

A MicroPython and CircuitPython library for controlling the SI5351 chip.
The library also supports generating quadrature output
using the phase offset feature of the chip.

# Introduction

The library file silicon5351.py provides the class SI5351\_I2C
you can use to control the Silicon Labs SI5351x range of chips.

This class also supports quadrature output.  However
the lowest frequency which can be outputted is limited by the chip hardware 
to clock's PLL frequency divided by 128.

## Example

```python
from silicon5351 import SI5351_I2C

# XIAO RP2040
import sys
if sys.implementation.name == 'circuitpython':
    import board, busio
    i2c = busio.I2C(board.SCL, board.SDA)
    while not i2c.try_lock():
        pass
else:
    import machine
    sda = machine.Pin(6)
    scl = machine.Pin(7)
    i2c = machine.I2C(1, sda=sda, scl=scl)

crystal = 25e6     # crystal frequency
mult = 15          # 15 * 25e6 = 375 MHz PLL frequency
freq = 3.0e6       # output frequency, upper limit 200MHz
quadrature = True  # lower limit for quadrature is 375MHz / 128
invert = False

si = SI5351_I2C(i2c, crystal=crystal)
si.init_clock(output=0, pll=0)
si.init_clock(output=1, pll=0, quadrature=quadrature, invert=invert)
si.setup_pll(pll=0, mult=mult)
si.set_freq(output=0, freq=freq) 
si.set_freq(output=1, freq=freq) 
si.enable_output(0)
si.enable_output(1)
print(f'done freq={freq} mult={mult} quadrature={quadrature} invert={invert}')
```

The library calls the PLL soft reset function 
of the chip whenever the MultiSynth whole number portion
of the divisor changes.  This is needed to generate quadrature
output.  It is also synchronizes all the outputs 
derived from a particular PLL.
In this way all outputs of a given PLL are forced to be coherrent
even if quadrature mode is not selected.  This can be demonstrated
by uncommenting the statement above with invert=True and commenting out
the statement with quadrature=quadrature.

## API

<code>class silicon5351.<b>SI5351\_I2C</b>(self, i2c, crystal, load=3, address=96)</code>  
Instantiate the SI5353\_I2C class.  All clock outputs (clkouts) will be shutdown and disabled.  
**i2c** The MicroPython or CircuitPython I2C object.  
**crystal** The crystal frequency in Hz.  
**load** The load capacitance of crystal.  Must use one of the global constants defined in the library for this value.  
**address** The I2C address of the si5351 chip.  

Instances of the <code>silicon5351.<b>SI5351\_I2C</b></code> class have the following public properties and methods:   

<code>SI5351\_I2C.<b>enable\_output</b>(self, output)</code>  
Enable the given clock output (clkout).  
**output** The clock output (clkout) to enable.  

<code>SI5351\_I2C.<b>disable\_output</b>(self, output)</code>  
Disable the given clock output (clkout).  
**output** The clock output (clkout) to disable.  

<code>SI5351\_I2C.<b>init\_clock</b>(self, output, pll, quadrature=False, invert=False, integer\_mode=False, drive\_strength=3)</code>  
Initialize the given clock output (clkout).
This method must be called before using set\_freq() on the output since
the library needs to know if the output has been setup for quadrature mode.  
**output** The number of the clock output (clkout) to initialize   
**pll** The number of the PLL to select. (0=PLLA, 1=PLLB)  
**invert** Whether the output should be inverted.  
**quadrature** Whether to enable quadrature output for this output.  
**integer\_mode** Whether to enable integer mode (MS or PLL) for this output.  
**drive\_strength** The drive strength in current to use for the output.  Must use one of the global constants defined in the library for this value.  

<code>SI5351\_I2C.<b>setup\_pll</b>(self, pll, mult, num=0, denom=1)</code>  
Set the frequency for the given PLL.
The PLL frequency is set to the frequency given by (mult + num / denom) times the crystal frequency.  
**pll** The number of the PLL to select. (0=PLLA, 1=PLLB)  
**mult** The whole number to multiply the crystal frequency by.  This value must be in the range [15-90].  
**num** The numerator to multiply the crystal frequency by. This value must be in the range [0-1048575).  
**denom** The denominator to multiply the crystal frequency by. This value must be in the range (0-1048575].  

<code>SI5351\_I2C.<b>set\_freq</b>(self, output, freq)</code>  
Set the frequency for the clock output (clkout).
Must call init\_clock() and setup\_pll() before calling this method.  
**output** The number of the clock output (clkout) to set the frequency for.  
**freq** The frequency in Hz to set the clock output (clkout) to.  

<code>SI5351\_I2C.<b>disabled\_states</b>(s0=0, s1=0, s2=0, s3=0, s4=0, s5=0, s6=0, s7=0)</code>  
Set the state of the clock outputs (clkout) when one or more clocks are disabled either in software or as a result of the output enable (OEB) pin going active.
The possible disabled states for an output are low, high, high impedance, and never disabled.  
**s0..s7** The disabled state to set for the appropriate clock output (clkout).  Must use one of the global constants defined in the library for this value.  

<code>SI5351\_I2C.<b>disable\_oeb</b>(self, mask)</code>  
Disable the output enable (OEB) pin for the given clock outputs (clkouts).  
**mask** A bit mask of the clock outputs (clkouts) to disable output enable (OEB) pin support for.  


