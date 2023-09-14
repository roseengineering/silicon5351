from silicon5351 import SI5351_CRYSTAL_LOAD_10PF, SI5351_I2C

def main():
    # XIAO RP2040
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
    mult = 32          # 32 * 25e6 = 800 MHz PLL frequency
    freq = 6.30e6      # frequency to output
    quadrature = True  # frequency limited to 800MHz/128

    freq = 6.251e6  # divisor = 127.9
    freq = 6.2987e6 # divisor = 127.01
    freq = 6.30e6   # divisor = 126.9

    # si5351
    si = SI5351_I2C(i2c, crystal=crystal)
    si.init_clock(output=0, pll=0)
    si.init_clock(output=1, pll=0, quadrature=quadrature)
    # si.init_clock(output=1, pll=0, invert=True)
    si.setup_pll(pll=0, mult=mult)
    si.set_freq(output=0, freq=freq) 
    si.set_freq(output=1, freq=freq) 
    si.enable_outputs(0x3)
    print('done')

if __name__ == "__main__":
    main()

