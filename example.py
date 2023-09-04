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
print('done')
