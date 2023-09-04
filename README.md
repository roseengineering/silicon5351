
# silicon5351

A micropython library for controlling the si5351 chip.
The library also supports generating quadrature output
using the phase offset feature of the chip.

# Introduction

The library file silicon5351.py provides the class SI5351\_I2C
which you can use to control the Silicon Labs SI5351x range of chips.

This class also supports quadrature output.  However
this support is limited by the chip hardware to the 
lower limit frequency of the clock's PLL frequency / 128.

Note, the library calls the PLL soft reset function 
of the chip whenever the MultiSynth whole number portion
of the divisor changes.  This is needed to generate quadrature
output.  But it is also synchronizes all the outputs 
derived from a particular PLL.
In this way all outputs of a given PLL are forced to be coherrent
even if quadrature mode is not selected.

## Example

```python
from silicon5351 import SI5351_CRYSTAL_LOAD_10PF, SI5351_I2C
import machine 

# i2c
sda = machine.Pin(6)
scl = machine.Pin(7)
i2c = machine.I2C(1, sda=sda, scl=scl)

crystal = 25e6     # crystal frequency
mult = 32          # 32 * 25e6 = 800 MHz PLL frequency
freq = 6.30e6      # frequency to output
quadrature = True  # frequency limited to 800MHz/128

# si5351
load = SI5351_CRYSTAL_LOAD_10PF
si = SI5351_I2C(i2c, crystal=crystal, load=load)

si.init_clock(output=0, pll=0)
si.init_clock(output=1, pll=0, quadrature=quadrature)
si.setup_pll(pll=0, mult=mult)
si.set_freq(output=0, freq=freq) 
si.set_freq(output=1, freq=freq) 
si.enable_outputs(0x3)
```

## API

<code>class silicon5351.<b>SI5351\_I2C</b>(self, i2c, crystal, load, address=96)</code>  
Instantiate the SI5353\_I2C class.  
**i2c** The micropython I2C object.  
**crystal** The crystal frequency in Hz.  
**load** The load capacitance of crystal.  Must use a predefined library constant for this capacitance value.  
**address** The I2C address of the si5351 chip.  

Instances of the <code>silicon5351.<b>SI5351\_I2C</b></code> class have the following public properties and methods:   

<code>SI5351\_I2C.<b>enable\_outputs</b>(self, mask)</code>  
Enable the given clock outputs (clkout).  
**mask** A bit mask of the clock outputs to enable.  

<code>SI5351\_I2C.<b>init\_clock</b>(self, output, pll, quadrature=False, invert=False, integer\_mode=False, drive\_strength=3)</code>  
Initialize the given clock output (clkout).
This method must be called before using set\_freq() on the output since
the library needs to know if the output has been setup for quadrature mode.  
**output** The number of the clock output to initialize   
**pll** The number of the PLL to select. (0=PLLA, 1=PLLB)  
**invert** Whether the output should be inverted.  
**quadrature** Whether to enable quadrature output for this output.  
**integer\_mode** Whether to enable integer mode (MS or PLL) for this output.  
**drive\_strength** The drive strength in current to use for the output.  Must use a predefined library constant for this current value.  

<code>SI5351\_I2C.<b>setup\_pll</b>(self, pll, mult, num=0, denom=1)</code>  
Set the frequency for the given PLL.
The PLL frequency is set to the frequency given by (whole + num / denom) times the crystal frequency.  
**pll** The number of the PLL to select. (0=PLLA, 1=PLLB)  
**mult** The whole number to multiply the crystal frequency by.  This value must be in the range [15-90].  
**num** The numerator to multiply the crystal frequency by. This value must be in the range [0-1048575).  
**denom** The denominator to multiply the crystal frequency by. This value must be in the range (0-1048575].  

<code>SI5351\_I2C.<b>set\_freq</b>(self, output, freq)</code>  
Set the frequency for the clock output (clkout).
Must call init\_clock() and setup\_pll() before calling this method.  
**output** The number of the clock output to set the frequency for.  
**freq** The frequency in Hz to set the clock output to.  

<code>SI5351\_I2C.<b>disabled\_states</b>(s0=0, s1=0, s2=0, s3=0, s4=0, s5=0, s6=0, s7=0)</code>  
Set the state of the clock outputs (clkout) when one or more clocks are disabled either in software or as a result of the OEB pin going active.
The possible disabled states for an output are low, high, high impedance, and never disabled.  
**s0..s7** The disabled state to set for the appropriate clock output.  Must use the predefined library constants for the state values.  

<code>SI5351\_I2C.<b>disable\_oeb</b>(self, mask)</code>  
Disable the output enable pin (OEB) for the given clock outputs (clkout).  
**mask** A bit mask of the clock outputs to disable OEB pin support for.  


