
SI5351_I2C_ADDRESS_DEFAULT    = 0x60

SI5351_CRYSTAL_LOAD_6PF       = (1<<6)
SI5351_CRYSTAL_LOAD_8PF       = (2<<6)
SI5351_CRYSTAL_LOAD_10PF      = (3<<6)

SI5351_CLK_DRIVE_STRENGTH_2MA = (0<<0)
SI5351_CLK_DRIVE_STRENGTH_4MA = (1<<0)
SI5351_CLK_DRIVE_STRENGTH_6MA = (2<<0)
SI5351_CLK_DRIVE_STRENGTH_8MA = (3<<0)

SI5351_DIS_STATE_LOW              = (0<<0)
SI5351_DIS_STATE_HIGH             = (1<<0)
SI5351_DIS_STATE_HIGH_IMPEDANCE   = (2<<0)
SI5351_DIS_STATE_NEVER_DISABLED   = (3<<0)


class SI5351_I2C:
    SI5351_MULTISYNTH_DIV_MAX_QUAD = 128
    SI5351_MULTISYNTH_DIV_MAX      = 2048
    SI5351_MULTISYNTH_C_MAX        = 1048575
    SI5351_CLK_POWERDOWN           = (1<<7)
    SI5351_PLL_RESET_A             = (1<<5)
    SI5351_PLL_RESET_B             = (1<<7)

    # clock
    SI5351_CLK_INPUT_MULTISYNTH_N  = (3<<2)
    SI5351_CLK_INTEGER_MODE        = (1<<6)
    SI5351_CLK_PLL_SELECT_A        = (0<<5)
    SI5351_CLK_PLL_SELECT_B        = (1<<5)
    SI5351_CLK_INVERT              = (1<<4)

    # registers
    SI5351_REGISTER_OUTPUT_ENABLE_CONTROL = 3
    SI5351_REGISTER_OEB_ENABLE_CONTROL    = 9
    SI5351_REGISTER_CLK0_CONTROL   = 16
    SI5351_REGISTER_DIS_STATE_1    = 24
    SI5351_REGISTER_DIS_STATE_2    = 25
    SI5351_REGISTER_PLL_A          = 26
    SI5351_REGISTER_PLL_B          = 34
    SI5351_REGISTER_MULTISYNTH0_PARAMETERS_1 = 42
    SI5351_REGISTER_MULTISYNTH1_PARAMETERS_1 = 50
    SI5351_REGISTER_MULTISYNTH2_PARAMETERS_1 = 58
    SI5351_REGISTER_CLK0_PHOFF     = 165
    SI5351_REGISTER_PLL_RESET      = 177
    SI5351_REGISTER_CRYSTAL_LOAD   = 183

    def write(self, register, value):
        self.write_bulk(register, [value])

    def write_bulk(self, register, values):
        self.i2c.writeto_mem(self.address, register, bytes(values))

    def write_config(self, reg, whole, num, denom, rdiv=0):
        # print('config',whole,num,denom)
        P1 = int(128 * whole + int(128.0 * num / denom) - 512)
        P2 = int(128 * num - denom * int(128.0 * num / denom))
        P3 = int(denom)
        self.write_bulk(reg, [ 
            (P3 & 0x0FF00) >> 8,
            (P3 & 0x000FF),
            (P1 & 0x30000) >> 16 | rdiv << 4,
            (P1 & 0x0FF00) >> 8,
            (P1 & 0x000FF),
            (P3 & 0xF0000) >> 12 | (P2 & 0xF0000) >> 16,
            (P2 & 0x0FF00) >> 8,
            (P2 & 0x000FF) ])

    def __init__(self, i2c, crystal, load, address=SI5351_I2C_ADDRESS_DEFAULT):
        """Instantiate the SI5353_I2C class.
        :param i2c The micropython I2C object.
        :param crystal The crystal frequency in Hz.
        :param load The load capacitance of crystal.  Must use a predefined library constant for this capacitance value.
        :param address The I2C address of the si5351 chip. 
        """
        self.i2c = i2c
        self.crystal = crystal
        self.address = address
        self.vco = {}
        self.pll = {}
        self.div = {}
        self.quadrature = {}
        self.write(self.SI5351_REGISTER_CRYSTAL_LOAD, load)
        # disable outputs and power down all 8 output drivers
        self.write(self.SI5351_REGISTER_OUTPUT_ENABLE_CONTROL, 0xFF)
        values = [ self.SI5351_CLK_POWERDOWN ] * 8
        self.write_bulk(self.SI5351_REGISTER_CLK0_CONTROL, values)

    def disabled_state(state):
        """Set the state of each clock output when disabled.
        The possible disabled states for an output are low, high, high impedance, and never disabled.
        :param state A list of states ordered by clock output (clkout) number.  Must use a predefined library constant for each of the state values in the list.
        """
        d = [ state[i] if i < len(state) else 0 for i in range(8) ]
        state_1 = d[3] << 6 | d[2] << 4 | d[1] << 2 | d[0]
        state_2 = d[7] << 6 | d[6] << 4 | d[5] << 2 | d[4]
        self.write(self.SI5351_REGISTER_DIS_STATE_1, state_1)
        self.write(self.SI5351_REGISTER_DIS_STATE_2, state_2)

    def disable_oeb(self, mask):
        """Disable the output enable pin (OEB) for the given clock outputs.
        :param mask A bit mask of the clock outputs (clkout) to disable OEB pin support for.
        """
        self.write(self.SI5351_REGISTER_OEB_ENABLE_CONTROL, mask & 0xFF)

    def enable_output(self, mask):
        """Enable the given clock outputs.
        :param mask A bit mask of the clock outputs (clkout) to enable.
        """
        self.write(self.SI5351_REGISTER_OUTPUT_ENABLE_CONTROL, ~mask & 0xFF)

    def init_clock(self, output, pll, 
                   quadrature=False, invert=False, integer_mode=False,
                   drive_strength=SI5351_CLK_DRIVE_STRENGTH_8MA):
        """Initialize the given clock output.
        This method must be called before using set_freq() on the output since 
        the library needs to know if the output has been setup for quadrature mode.
        :param output The number of the clock output (clkout) to initialize 
        :param pll The number of the PLL to select. (0=PLLA, 1=PLLB)
        :param invert Whether the output should be inverted.
        :param quadrature Whether to enable quadrature output for this output.
        :param integer_mode Whether to enable integer mode (MS or PLL) for this output.
        :param drive_strength The drive strength in current to use for the output.  Must use a predefined library constant for this current value.
        """
        value = drive_strength 
        value |= self.SI5351_CLK_INPUT_MULTISYNTH_N
        if integer_mode: value |= SI5351_CLK_INTEGER_MODE
        if quadrature or invert: value |= self.SI5351_CLK_INVERT
        if pll == 0: value |= self.SI5351_CLK_PLL_SELECT_A
        if pll == 1: value |= self.SI5351_CLK_PLL_SELECT_B
        self.write(self.SI5351_REGISTER_CLK0_CONTROL + output, value)
        self.set_phase(output, 0)
        self.quadrature[output] = quadrature
        self.pll[output] = pll

    def setup_pll(self, pll, mult, num=0, denom=1):
        """Set the frequency for the given PLL.
        The PLL frequency is set to the frequency given by (whole + num / denom) times the crystal frequency.
        :param pll The number of the PLL to select. (0=PLLA, 1=PLLB)
        :param mult The whole number to multiply the crystal frequency by.  This value must be in the range [15-90].
        :param num The numerator to multiply the crystal frequency by. This value must be in the range [0-1048575).
        :param denom The denominator to multiply the crystal frequency by. This value must be in the range (0-1048575].
        """
        # print('setup_pll',pll,mult,'+',num,'/',denom)
        vco = self.crystal * (mult + num / denom)
        if pll == 0: reg = self.SI5351_REGISTER_PLL_A
        if pll == 1: reg = self.SI5351_REGISTER_PLL_B
        self.write_config(reg, mult, num, denom)
        self.vco[pll] = vco

    def set_freq(self, output, freq):
        """Set the frequency for the clock output.
        Must call init_clock() and setup_pll() before calling this method.
        :param output The number of the clock output (clkout) to set the frequency for.
        :param freq The frequency in Hz to set the clock output to.
        """
        # print('set_freq',output,pll,freq,'vco=',self.vco[pll],'div=',self.vco[pll]/freq)
        pll = self.pll[output]
        vco = self.vco[pll]
        for rdiv in range(8): 
            if freq > vco / self.SI5351_MULTISYNTH_DIV_MAX: break
            freq *= 2
        div = vco // freq
        max_denom = self.SI5351_MULTISYNTH_C_MAX # for quadrature max is 128
        num, denom = self.approximate_fraction(vco % freq, freq, max_denom)
        self.setup_multisynth(output, pll, div, num, denom, rdiv=rdiv) # do first
        if self.div.get(output) != div:
            if self.quadrature[output]: self.set_phase(output, div)
            self.reset_pll(pll) # syncs all clocks derived from this pll 
            self.div[output] = div

    def set_phase(self, output, div):
        # print('phase',output,div)
        self.write(self.SI5351_REGISTER_CLK0_PHOFF + output, int(div) & 0xFF)

    def reset_pll(self, pll):
        # print('soft reset pll',pll)
        if pll == 0: value = self.SI5351_PLL_RESET_A 
        if pll == 1: value = self.SI5351_PLL_RESET_B
        self.write(self.SI5351_REGISTER_PLL_RESET, value)

    def approximate_fraction(self, n, d, max_denom):
        # cf. https://github.com/python/cpython/blob/master/Lib/fractions.py#L227
        denom = d;
        if denom > max_denom:
            num = n
            p0 = 0; q0 = 1; p1 = 1; q1 = 0
            while denom != 0:
                a = num // denom
                b = num % denom
                q2 = q0 + a * q1
                if q2 > max_denom:
                    break
                p2 = p0 + a * p1
                p0 = p1; q0 = q1; p1 = p2; q1 = q2
                num = denom; denom = b
            n = p1; d = q1
        return n, d

    def setup_multisynth(self, output, pll, div, num, denom, rdiv):
        # print('setup_multisynth',output,pll,div,'+',num,'/',denom,'rdiv=',rdiv)
        if output == 0: reg = self.SI5351_REGISTER_MULTISYNTH0_PARAMETERS_1
        if output == 1: reg = self.SI5351_REGISTER_MULTISYNTH1_PARAMETERS_1
        if output == 2: reg = self.SI5351_REGISTER_MULTISYNTH2_PARAMETERS_1
        self.write_config(reg, div, num, denom, rdiv=rdiv)


if __name__ == '__main__':
    import machine

    # i2c
    sda = machine.Pin(6)
    scl = machine.Pin(7)
    i2c = machine.I2C(1, sda=sda, scl=scl)

    # si5351
    crystal = 25e6
    load = SI5351_CRYSTAL_LOAD_10PF
    si = SI5351_I2C(i2c, crystal=crystal, load=load)

    mult = 32
    freq = 6.30e6  # 126.9
    freq = 6.2987e6 # 127.01
    freq = 6.251e6 # 127.9
    freq = 100e3
    quadrature = True
    quadrature = False
    si.init_clock(output=0, pll=0)
    si.init_clock(output=1, pll=0, quadrature=quadrature) #, invert=True)
    si.setup_pll(pll=0, mult=mult)
    si.set_freq(output=0, freq=freq) 
    si.set_freq(output=1, freq=freq) 
    si.enable_output(0x3)

    # led
    led_blue = machine.Pin(25, machine.Pin.OUT)
    led_blue.value(0)    



