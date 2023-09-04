
# silicon

A micropython library for controlling the si5351 chip 
and with quadrature output support.

# introduction

The library file silicon5351.py provides the class SI5351\_I2C
which you can use to control the Silicon Labs SI5351x range of chips.

This class also supports quadrature output.  However
this support is limited by the chip hardware to the 
lower limit frequency of the clock's PLL frequency / 128.

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
si.enable_output(0x3)
```

## API

<code>class silicon5351.<b>SI5351\_I2C</b>(self, i2c, crystal, load, address=96)</code>  
Instantiate SI5353\_I2C class.  
**i2c** the micropython I2C object.  
**crystal** the crystal frequency in Hz.  
**load** the load capacitance of crystal.  Must use a predefined library constant for this capacitance value.  
**address** the I2C address of the si5351 chip.  

Instances of the <code>silicon5351.<b>SI5351\_I2C</b></code> class have the following properties and methods:   

<code>SI5351\_I2C.<b>disabled\_state</b>(state)</code>  
Set the state of each clock output when disabled.
The possible disabled states for an output are low, high, high impedance, and never disabled.  
**state** a list of states ordered by clock output (clkout) number.  Must use a predefined library constant for this state value.  

<code>SI5351\_I2C.<b>disable\_oeb</b>(self, mask)</code>  
Disable the output enable pin (OEB) for the clocks.  
**mask** a bit mask of the clock outputs (clkout) to disable OEB pin support for.  

<code>SI5351\_I2C.<b>enable\_output</b>(self, mask)</code>  
Enable the clock output pins  
**mask** a bit mask of the clock outputs (clkout) to enable.  

<code>SI5351\_I2C.<b>init\_clock</b>(self, output, pll, quadrature=False, invert=False, integer\_mode=False, drive\_strength=3)</code>  
Initialize the given clock output
This method must be called before using set\_freq() on the output since
the library needs to know if the output has been setup for quadrature mode.  
**output** the number of the clock output (clkout) to initialize   
**pll** the number of the PLL to select. (0=PLLA, 1=PLLB)  
**invert** whether the output should be inverted.  
**quadrature** enable quadrature output for the output.  
**integer\_mode** enable integer mode (MS or PLL) for the output.  
**drive\_strength** the drive strength in current to use for the output.  Must usea predefined library constant for this current value.  

<code>SI5351\_I2C.<b>setup\_pll</b>(self, pll, mult, num=0, denom=1)</code>  
Set the frequency for the given PLL.  
**pll** the number of the PLL to select. (0=PLLA, 1=PLLB)  
**mult** the whole number to multiply the crystal frequency by.  This value must be in the range [15-90].  
**num** the numerator to multiply the crystal frequency by. This value must be in the range [0-1048575).  
**denom** the denominator to multiply the crystal frequency by. This value must be in the range (0-1048575].  

<code>SI5351\_I2C.<b>set\_freq</b>(self, output, freq)</code>  
Set the frequency for the clock output
Must call init\_clock() and setup\_pll() for calling this method.  
**output** the number of the clock output (clkout) to set frequency for.  
**freq** the frequency to set in Hz.  


