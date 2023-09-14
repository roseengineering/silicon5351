
import sys, inspect, re, subprocess
sys.path.append('.')

def run(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return f'{result.stdout.rstrip()}'


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
                text.append(f'Instances of the <code>{package}.<b>{classname}</b></code> class have the following public properties and methods:   ')
                text.append('')
    text = [ ln.replace('_', '\_') for ln in text ]
    return '\n'.join(text)


print(f"""\

# silicon5351

A MicroPython and CircuitPython library for controlling the SI5351 chip.
The library also supports generating quadrature output
using the phase offset feature of the chip.

# Introduction

The library file silicon5351.py provides the class SI5351\_I2C
which you can use to control the Silicon Labs SI5351x range of chips.

This class also supports quadrature output.  However
this support is limited by the chip hardware to the 
lower limit frequency of the clock's PLL frequency / 128.

## Example

```python
{run("cat example.py")}
```

The library calls the PLL soft reset function 
of the chip whenever the MultiSynth whole number portion
of the divisor changes.  This is needed to generate quadrature
output.  But it is also synchronizes all the outputs 
derived from a particular PLL.
In this way all outputs of a given PLL are forced to be coherrent
even if quadrature mode is not selected.  This can be demonstrated
by uncommenting the statement with invert=True and commenting out
the statement with quadrature=quadrature.

## API

{generate_docs('silicon5351')}
""")


