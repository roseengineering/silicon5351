
# silicon5351

A MicroPython and CircuitPython library for controlling the SI5351 chip.

# Introduction

The file silicon5351.py contains the actual si5351 library. Inside the library
is the SI5351\_I2C class for controlling the Silicon Labs SI5351x range of chips.

This class also supports the quadrature output feature of the chip.  The lowest 
frequency that can be generated in quadrature is limited by the chip hardware 
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
mul = 15           # 15 * 25e6 = 375 MHz PLL frequency
freq = 3.0e6       # output frequency with an upper limit 200MHz
quadrature = True  # lower limit for quadrature is 375MHz / 128
invert = False     # invert option ignored when quadrature is true

si = SI5351_I2C(i2c, crystal=crystal)
si.setup_pll(pll=0, mul=mul)
si.init_clock(output=0, pll=0)
si.init_clock(output=1, pll=0, quadrature=quadrature, invert=invert)
si.set_freq_fixedpll(output=0, freq=freq) 
si.set_freq_fixedpll(output=1, freq=freq) 
si.enable_output(output=0)
si.enable_output(output=1)
print(f'done freq={freq} mul={mul} quadrature={quadrature} invert={invert}')
```
The library calls the PLL soft reset function 
of the chip whenever the MultiSynth whole number portion
of the divisor changes or is intitialized.
This soft reset is required in order to generate a quadrature
or an inverted output.  It is also required to synchronize all outputs 
derived off a particular PLL and be coherrent with respect to each other.

## API

<code>class silicon5351.<b>SI5351\_I2C</b>(self, i2c, crystal, load=3, address=96)</code>  
Instantiate the SI5353\_I2C class.  All clock outputs
(clkouts) will be shutdown and disabled.  
**i2c** The MicroPython or CircuitPython I2C object.  
**crystal** The crystal frequency in Hz.  
**load** The load capacitance of crystal.  Must use one of 
the global constants defined in the library for this value.  
**address** The I2C address of the si5351 chip.

Instances of the <code>silicon5351.<b>SI5351\_I2C</b></code> class have the following public properties and methods:   

<code>SI5351\_I2C.<b>init\_clock</b>(self, output, pll, quadrature=False, invert=False, drive\_strength=3)</code>  
Initialize the given clock output (clkout).
This method must be called before using set\_freq\_fixedpll() on
the output.  
**output** The number of the clock output (clkout) to initialize   
**pll** The number of the PLL to select. (0=PLLA, 1=PLLB)  
**invert** Invert the output.  
**quadrature** Invert the output and also enable quadrature 
logic in the library.  
**drive\_strength** The drive strength in current to use 
for the output. Must use one of the global constants defined
in the library for this value.

<code>SI5351\_I2C.<b>enable\_output</b>(self, output)</code>  
Enable the given clock output (clkout).  
**output** The clock output (clkout) to enable.

<code>SI5351\_I2C.<b>disable\_output</b>(self, output)</code>  
Disable the given clock output (clkout).  
**output** The clock output (clkout) to disable.

<code>SI5351\_I2C.<b>setup\_pll</b>(self, pll, mul, num=0, denom=1)</code>  
Set the frequency for the given PLL.
The PLL frequency is set to the frequency given by
(mul + num / denom) times the crystal frequency.  
**pll** The number of the PLL to select. (0=PLLA, 1=PLLB)  
**mul** The whole number to multiply the crystal frequency 
by.  This value must be in the range [15-90].  
**num** The numerator to multiply the crystal frequency 
by. This value must be in the range [0-1048574].  
**denom** The denominator to multiply the crystal frequency by.
This value must be in the range [1-1048575].

<code>SI5351\_I2C.<b>setup\_multisynth</b>(self, output, div, num=0, denom=1, rdiv=0)</code>  
Set the multisynth divisor of the PLL frequency.  
**output** The number of the clock output (clkout) to 
set the frequency for.  
**div** The whole number divisor to set the multisynth to.
This value must be in the range [4-2047]  
**num** The numerator to divide the pll frequency by. 
This value must be in the range [0-1048574].  
**denom** The denominator to divide the pll frequency by. 
This value must be in the range [1-1048575].  
**rdiv** The Rx divisor in log base 2 for additional vco division.

<code>SI5351\_I2C.<b>set\_freq\_fixedpll</b>(self, output, freq)</code>  
Set the frequency for the clock output (clkout) by changing
the multisynth divisors.  The pll frequency is unchanged.
Must call init\_clock() and setup\_pll() before calling this method.
The maximum frequency that can be generated is the vco frequency
divided by 8.  
**output** The number of the clock output (clkout) to 
set the frequency for.  
**freq** The frequency in Hz to set the clock output (clkout) to.

<code>SI5351\_I2C.<b>set\_freq\_fixedms</b>(self, output, freq)</code>  
Set the clock output (clkout) to the requested frequency by
changing the pll multiplier value.  The multisynth divisor is
set to a whole number given by div.  Must call init\_clock() and
setup\_multisynth() before calling this method to set the.  The
minimum frequency that can be generated is the minimum frequency
of the pll divided by div.  The maximum frequency that can be
generated is the maximum frequency of the pll divided by div.  
**output** The number of the clock output (clkout) to 
set the frequency for.  
**freq** The frequency in Hz to set the clock output (clkout) to.

<code>SI5351\_I2C.<b>disabled\_states</b>(self, output, state)</code>  
Set the state of the clock outputs (clkout) when one
or more clocks are disabled either in software or
as a result of the output enable (OEB) pin going active.
The possible disabled states for an output are low voltage, high
voltage, high impedance, and never disabled.  
**output** The clock output (clkout) to set the disabled state for.  
**state** The disabled state to set for the clock 
output (clkout).  Must use one of the global constants defined in
the library for this value.

<code>SI5351\_I2C.<b>disable\_oeb</b>(self, mask)</code>  
Disable the output enable (OEB) pin for the given
clock outputs (clkouts).  
**mask** A bit mask of the clock outputs (clkouts) to disable 
output enable (OEB) pin support for.


