""" Rigol DS1052E Oscilloscope """

import time
import numpy as np
import matplotlib.pyplot as plt

from .visa import Instrument
import asmr.logging


#:::: Logging
#::::::::::::
log = asmr.logging.get_logger()


# Resources:
# https://stackoverflow.com/questions/66480203/pyvisa-not-listing-usb-instrument-on-linux
# https://www.batronix.com/pdf/Rigol/ProgrammingGuide/DS1000DE_ProgrammingGuide_EN.pdf
# https://web.archive.org/web/20230131210803/http://nnp.ucsd.edu/Lab_Equip_Manuals/Rigol_DS1000_Progr_Manu.pdf
# https://www.cibomahto.com/2010/04/controlling-a-rigol-oscilloscope-using-linux-and-python/
# https://gist.github.com/pklaus/7e4cbac1009b668eafab
# https://github.com/wd5gnr/qrigol/blob/master/scopedata.cpp#L216

class RigolDS1052E(Instrument):
    id = 'USB0::6833::1416::DS1ET171605654\x00::0::INSTR'


    def __init__(self):
        super().__init__(self.id)
        self.scope = self.resource
        self.channel_data = [None, None]
        self.channel_time_unit = ["S", "S"]

        # set internal memory to long
        if self.scope.query(":ACQ:MEMD?") != 'NORMal':
            self.scope.write(":ACQ:MEMD NORMal")
            time.sleep(1)

    def collect(self, filename, plot=False):
        # open file
        fd = open(filename, 'w')
        self.snapshot_idx = 0

        log.info("Press ctrl-c to stop collecting data")
        try:
            while True:
                self.snapshot_waveforms()
                self.write_to_csv(fd)
                if plot:
                    self.plot()
                    time.sleep(1)
        except KeyboardInterrupt:
            log.info("Done collecting data")

        self.scope.write(":RUN")
        self.scope.write(":KEY:FORCE")
        fd.close()

    def plot(self, filename=None):
        if filename != None:
            fd = open(filename, 'r')
            idx = 0
            self.read_csv(fd, idx)
        else:
            if self.channel_data[0] == None or self.channel_data[1] == None:
                self.snapshot_waveforms()

        # plot stuff
        x = self.channel_data[0][0]
        chan1 = self.channel_data[0][1]
        chan2 = self.channel_data[1][1]
        plt.style.use('dark_background')

        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx()
        ax1.plot(x, chan1, 'y-')
        ax2.plot(x, chan2, 'b-')

        plt.title("Oscilloscope Measurements")
        ax1.set_xlabel("Time (" + self.channel_time_unit[0] + ")")
        ax1.set_ylabel("Voltage (V) [Channel 1]", color='y')
        ax2.set_ylabel("Voltage (V) [Channel 2]", color='b')

        plt.xlim(x[0], x[-1])
        plt.show()

    def read_csv(self, fd, idx):
        for i in range(0, idx+1):
            line = fd.readline()
            if (i == idx):
                # channel 1
                line = line.split(",")
                tUnit = line[2]
                data = np.asarray(line[3:], dtype='float')
                self.channel_data[0] = [data[0::2], data[1::2]]
                # channel 2
                line = fd.readline()
                line = line.split(",")
                tUnit = line[2]
                data = np.asarray(line[3:], dtype='float')
                self.channel_data[1] = [data[0::2], data[1::2]]
                return


    def write_to_csv(self, fd):
        """ write (append) data to csv:
        <snapshot#>, <chan>, <timeUnit>, <time0>, <sample0>, ...
        """
        for i in range(0, 2):
            preamble = f"{self.snapshot_idx},{i},{self.channel_time_unit[i]}"
            data = self.channel_data[i][1]
            timeline =  self.channel_data[i][0]
            interleaved = np.empty((data.size + timeline.size,), dtype=data.dtype)
            interleaved[0::2] = timeline
            interleaved[1::2] = data

            line = preamble + "," + ",".join(np.char.mod('%f', interleaved)) + "\n"
            fd.write(line)
        self.snapshot_idx += 1


    def snapshot_waveforms(self, chan: int = -1):
        chan_min = 2 if chan == 2 else 1
        chan_max = 1 if chan == 1 else 2

        for i in range(chan_min, chan_max + 1):
            self._snapshot_waveform(i)

    def _snapshot_waveform(self, chan: int):
        self.scope.write(":STOP")

        # wait for internal oscope memory to fill
        time.sleep(0.5)

        # Get the timescale
        timescale = float(self.scope.query(":TIM:SCAL?"))

        # Get the timescale offset
        timeoffset = float(self.scope.query(":TIM:OFFS?"))
        voltscale = float(self.scope.query(f":CHAN{chan}:SCAL?"))

        # And the voltage offset
        voltoffset = float(self.scope.query(f":CHAN{chan}:OFFS?"))

        # set waveform acquisition to raw mode
        self.scope.write(":WAV:POIN:MODE RAW")

        # B stands for one byte (https://docs.python.org/3/library/struct.html#format-characters)
        data = self.scope.query_binary_values(
            f":WAV:DATA? CHAN{chan}",
            datatype='B',
            container=np.array
        )
        data_size = len(data)
        sample_rate = self.scope.query(f":ACQ:SAMP? CHAN{chan}")
        log.debug(f"Data size: {data_size} Samplerate: {sample_rate}")

        self.scope.write(":RUN")
        self.scope.write(":KEY:FORCE")

        # invert data
        data = data * -1. + 255.

        # scope display is 30-299, so shift by 130 - voltage in counts, then scale to voltage
        data = (data - 130.0 - voltoffset/voltscale*25) / 25 * voltscale

        # generate a time axis.
        timeline = np.linspace(timeoffset - 6 * timescale, timeoffset + 6 * timescale, num=len(data))

        tUnit = "S"
        if (timeline[-1] < 1e-3):
            timeline = timeline * 1e6
            tUnit = "uS"
        elif (timeline[-1] < 1):
            timeline = timeline * 1e3
            tUnit = "mS"

        self.channel_data[chan-1] = [timeline, data]
        self.channel_time_unit[chan-1] = tUnit
