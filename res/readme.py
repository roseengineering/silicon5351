
import sys, inspect, re, subprocess
sys.path.append('.')

def run(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return f'{command}\n{result.stdout.rstrip()}'


def generate_docs(package, data=None, classname=None, text=[]):
    if data is None:
        __import__(package)
        mod = sys.modules[package]
        data = { k:v for k,v in mod.__dict__.items() if k[0] != '_' }
    for k, fn in data.items():
        if k == '__module__': continue
        if k == '__weakref__': continue
        if k == '__dict__': continue
        if isinstance(fn, type):
            generate_docs(package, fn.__dict__, k, text)
        else:
            if not fn.__doc__:
                continue
            if isinstance(fn, property):
                text.append(f'<code>{classname}.<b>{k}</b></code>') # property
            else:
                try:
                    signature = inspect.signature(fn)
                except TypeError:
                    continue
                if k == '__init__':  # constructor
                    text.append(f'<code>class {package}.<b>{classname}</b>{signature}</code>  ')
                elif classname is None: # function
                    text.append(f'<code>{package}.<b>{k}</b>{signature}</code>  ')
                else:  # method
                    text.append(f'<code>{classname}.<b>{k}</b>{signature}</code>  ')
            inbody = True
            for ln in fn.__doc__.strip().splitlines():
                m_param = re.search(':param\s+(\S+)\s+(.*)', ln)
                m_return = re.search(':return\s+(.*)', ln)
                if m_param or m_return:
                    if inbody: text[-1] += '  '
                    inbody = False
                if m_param:
                    text.append(f'**{m_param.group(1)}** {m_param.group(2)}  ')
                elif m_return:
                    text.append(f'**returns** {m_return.group(1)}  ')
                else:
                    text.append(ln.strip())
            text.append('')
            if k == '__init__':
                text.append(f'Instances of the <code>{package}.<b>{classname}</b></code> class have the following properties and methods:   ')
                text.append('')
    text = [ ln.replace('_', '\_') for ln in text ]
    return '\n'.join(text)


print(f"""\

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

{generate_docs('silicon5351')}
""")


