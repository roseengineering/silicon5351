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
invert = False     # invert has no effect in quadrature mode

si = SI5351_I2C(i2c, crystal=crystal)
si.init_clock(output=0, pll=0)
si.init_clock(output=1, pll=0, quadrature=quadrature, invert=invert)
si.setup_pll(pll=0, mult=mult)
si.set_freq(output=0, freq=freq) 
si.set_freq(output=1, freq=freq) 
si.enable_output(0)
si.enable_output(1)
print(f'done freq={freq} mult={mult} quadrature={quadrature} invert={invert}')


