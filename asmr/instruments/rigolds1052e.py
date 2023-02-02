""" Rigol DS1052E Oscilloscope """

from dataclasses import dataclass, field
import time
import numpy as np
import numpy.typing as npt
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

@dataclass
class SnapShot:
    timeUnit: str = field(init=False)
    time: npt.NDArray = field(init=False)
    chan1: npt.NDArray = field(init=False)
    chan2: npt.NDArray = field(init=False)
    chan1_vpp: float = field(init=False)
    chan2_vpp: float = field(init=False)


def load_snapshots(filename: str):
    snapshots = []
    snapshot = None
    idx = 0

    with open(filename) as fd:
        for line in fd:
            line = line.split(",")
            data = np.asarray(line[4:], dtype='float')

            if idx%2 == 0:
                snapshot = SnapShot()
                snapshot.timeUnit = line[2]
                snapshot.chan1_vpp = line[3]
                snapshot.time = data[0::2]
                snapshot.chan1 = data[1::2]
            else:
                snapshot.chan2 = data[1::2]
                snapshot.chan2_vpp = line[3]
                snapshots.append(snapshot)

            idx += 1

    return snapshots


class RigolDS1052E(Instrument):
    id = 'USB0::6833::1416::DS1ET171605654\x00::0::INSTR'

    def __init__(self):
        super().__init__(self.id)
        self.scope = self.resource
        self.snapshots = []

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
                self.write_to_csv(fd, self.snapshots[-1])
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
            self.snapshots = load_snapshots(filename)
        else:
            if len(self.snapshots) == 0:
                self.snapshot_waveforms()

        # plot stuff
        t = self.snapshots[-1].time
        tUnit = self.snapshots[-1].timeUnit
        chan1 = self.snapshots[-1].chan1
        chan2 = self.snapshots[-1].chan2

        plt.style.use('dark_background')

        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx()
        ax1.plot(t, chan1, 'y-')
        ax2.plot(t, chan2, 'b-')

        plt.title("Oscilloscope Measurements")
        ax1.set_xlabel("Time (" + tUnit + ")")
        ax1.set_ylabel("Voltage (V) [Channel 1]", color='y')
        ax2.set_ylabel("Voltage (V) [Channel 2]", color='b')

        plt.xlim(t[0], t[-1])
        plt.show()

    def write_to_csv(self, fd, snapshot):
        """ write (append) data to csv:
        <snapshot#>, <chan>, <timeUnit>, <vpp>, <time0>, <sample0>, ...
        """
        for i in range(0, 2):
            preamble = f"{self.snapshot_idx},{i},{snapshot.timeUnit}"
            vpp = snapshot.chan1_vpp if i%2 == 0 else snapshot.chan2_vpp
            data = snapshot.chan1 if i%2 == 0 else snapshot.chan2
            timeline =  snapshot.time
            interleaved = np.empty((data.size + timeline.size,), dtype=data.dtype)
            interleaved[0::2] = timeline
            interleaved[1::2] = data

            line = preamble + f",{vpp}" + "," + ",".join(np.char.mod('%f', interleaved)) + "\n"
            fd.write(line)
        self.snapshot_idx += 1


    def snapshot_waveforms(self, chan: int = -1):
        chan_min = 2 if chan == 2 else 1
        chan_max = 1 if chan == 1 else 2

        snapshot = SnapShot()
        for i in range(chan_min, chan_max + 1):
            snapshot = self._snapshot_waveform(i, snapshot)
        self.snapshots.append(snapshot)

    def _snapshot_waveform(self, chan: int, snapshot):
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

        # measure the voltage peak-to-peak value
        vpp = float(self.scope.query(f":MEASure:VPP? CHAN{chan}"))

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
        log.debug(f"Data size: {data_size} Samplerate: {sample_rate} Vpp: {vpp}")

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


        snapshot.timeUnit = tUnit
        snapshot.time = timeline
        if chan == 1:
            snapshot.chan1 = data
            snapshot.chan1_vpp = vpp
        else:
            snapshot.chan2 = data
            snapshot.chan2_vpp = vpp

        return snapshot
