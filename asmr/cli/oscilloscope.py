""" Oscilloscope Tools """

import sys

import click
import pyvisa
import numpy as np
import matplotlib.pyplot as plt

# notes
# previously the usb device wasnt recognized as a usbtmc device, but after
# following the recommendations in:
# https://stackoverflow.com/questions/66480203/pyvisa-not-listing-usb-instrument-on-linux
# it worked!

# for commands see:
# https://web.archive.org/web/20230131210803/http://nnp.ucsd.edu/Lab_Equip_Manuals/Rigol_DS1000_Progr_Manu.pdf
# also see:
# https://www.cibomahto.com/2010/04/controlling-a-rigol-oscilloscope-using-linux-and-python/
# also see:
# https://gist.github.com/pklaus/7e4cbac1009b668eafab

RIGOL_INSTR_ID = '::DS1ET' #'USB0::6833::1416::DS1ET171605654\x00::0::INSTR'

rm = pyvisa.ResourceManager('@py')
instruments = rm.list_resources()
usb = list(filter(lambda x: RIGOL_INSTR_ID in x, instruments))
if len(usb) != 1:
    print('Oscilloscope Not Connected!', instruments)
    sys.exit(-1)
scope = rm.open_resource(usb[0])#, timeout=20, chunk_size=1024000) # bigger timeout for long mem

def plot():
    # Grab the raw data from channel 2
    scope.write(":STOP")

    # Get the timescale
    timescale = float(scope.query(":TIM:SCAL?"))

    # Get the timescale offset
    timeoffset = float(scope.query(":TIM:OFFS?"))
    voltscale = float(scope.query(':CHAN2:SCAL?'))

    # And the voltage offset
    voltoffset = float(scope.query(":CHAN2:OFFS?"))

    scope.write(":WAV:POIN:MODE RAW")
    # B stands for one byte
    # see:
    # https://docs.python.org/3/library/struct.html#format-characters
    data = scope.query_binary_values(":WAV:DATA? CHAN2",  datatype='B', container=np.array)
    data_size = len(data)
    sample_rate = scope.query(':ACQ:SAMP?')[0]
    print('Data size:', data_size, "Sample rate:", sample_rate)

    scope.write(":RUN")
    scope.write(":KEY:FORCE")
    scope.close()

    # Walk through the data, and map it to actual voltages
    # This mapping is from Cibo Mahto
    # First invert the data
    data = data * -1. + 255.

    # Now, we know from experimentation that the scope display range is actually
    # 30-229.  So shift by 130 - the voltage offset in counts, then scale to
    # get the actual voltage.
    data = (data - 130.0 - voltoffset/voltscale*25) / 25 * voltscale

    # Now, generate a time axis.
    time = np.linspace(timeoffset - 6 * timescale, timeoffset + 6 * timescale, num=len(data))

    # See if we should use a different time axis
    if (time[-1] < 1e-3):
        time = time * 1e6
        tUnit = "uS"
    elif (time[-1] < 1):
        time = time * 1e3
        tUnit = "mS"
    else:
        tUnit = "S"

    # Plot the data
    plt.plot(time, data)
    plt.title("Oscilloscope Channel 1")
    plt.ylabel("Voltage (V)")
    plt.xlabel("Time (" + tUnit + ")")
    plt.xlim(time[0], time[-1])
    plt.show()

@click.group("scope", help="oscilloscope tools", invoke_without_command=True)
@click.pass_context
def main(ctx):
    if ctx.invoked_subcommand is None:
        plot()  # default command.
