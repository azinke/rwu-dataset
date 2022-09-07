"""Calibration module."""
import numpy as np

import os
import json
from core.config import ROOTDIR
from core.utils.common import error


class AntennaConfig:
    """Antenna configuration.

    Attributes:
        num_rx (int): Number of reception antenna
        num_tx (int): Number of transmission antenna
        fdesign (float): Base frequency the sensor has been designed for
        rxl (NDArray): Array describing the configuration of the
            reception antenna in unit of half-wavelengths
        txl (NDArray): Array describing the configuration of the
            transmission antenna in unit of half-wavelengths

    NOTE:
        The 'rxl' and 'txl' arrays describe the antenna layout using the
        followinf structure [idx az, el].

        Thus, the first column indicates the index number of the array.
        The second is the azimuth position of each antenna in half a wave
        length and the last column their elevation position.

        It's important to keep in mind that the row wise ordering of those
        matrices is [dev4, dev1, dev3, dev2] for the cascade radar.
    """

    def __init__(self, filepath: str) -> None:
        """Init Antenna config.

        Argument:
            filepath: Path to the antenna configuration file
        """
        config = {}
        with open(os.path.join(ROOTDIR, filepath), "r") as fh:
            config = json.load(fh)
        self.nrx = config["nrx"]
        self.ntx = config["ntx"]
        self.fdesign = config["fdesign"]    # in GHz
        self.rxl = np.array(config["rxl"])  # RX layout
        self.txl = np.array(config["txl"])  # TX layout


class CouplingCalibration:
    """Coupling calibration.

    Attributes:
        nrx (int): Number of reception antenna
        ntx (int): Number of transmission antenna
        ns (int): Number of ADC samples
        data (NDArray): Matrix describing the coupling calibartion
    """

    def __init__(self, filepath: str) -> None:
        """Init coupling calibration."""
        with open(os.path.join(ROOTDIR, filepath), "r") as fh:
            config = json.load(fh)
        self.nrx = config["nrx"]
        self.ntx = config["ntx"]

        binfile: str = os.sep.join([*filepath.split("/")[:-1], config["data"]])
        binfile = os.path.join(ROOTDIR, binfile)
        self.data = np.fromfile(binfile, dtype=np.float32, count=-1)
        self.data = self.data.reshape(self.ntx, self.nrx, 2)
        self.data = self.data[:, :, 0] + 1j * self.data[:, :, 1]
        self.data = self.data.reshape(self.ntx, self.nrx, 1, 1)


class HeatmapConfiguration:
    """Heatmap configuration.

    Attributes:
        num_range_bins (int): Number of range bins
        num_elevation_bins (int): Number of elevation bins
        num_azimuth_bins (int): Number of azimuth bins
        range_bin_width (float): Width of range bin - range resolution
        azimuth_bins (list[float]): Array describing the azimuth bin
        elevation_bins (list[float]): Array describing the elevation bin
    """

    def __init__(self, filepath: str) -> None:
        """Init heatmap configuration."""
        with open(os.path.join(ROOTDIR, filepath), "r") as fh:
            # Load heatmap setup file
            pass


class WaveformConfiguration:
    """Waveform configuration.

    Attributes:
        nrx (int): Number of reception antenna
        ntx (int): Number of transmission antenna
        ns (int): Number of ADC samples per chirp
        nc (int):  Number of chirp loops per frame
        ns (float): ADC sampling frequency in herz
        fstart (float): Chirp start frequency in herz
        fslope (float): Frequency slope in Hz/s
        fsample (float): ADC sampling frequency in Hz
        idle_time (float): Idle time before starting a new chirp in second
        adc_start_time (float): Start time of ADC in second
        ramp_end_time (float): End time of frequency ramp
    """

    def __init__(self, filepath: str) -> None:
        """Init waveform configuration."""
        config = {}
        with open(filepath, "r") as fh:
            config = json.load(fh)
        self.nrx = config["numRx"]
        self.ntx = config["numTx"]
        self.ns = config["numAdcSamples"]
        self.nc = config["numLoops"]
        self.fstart = config["startFrequency_Ghz"] * 1e+9
        self.fsample = config["samplingFequency_ksps"] * 1e+3
        self.fslope = config["frequencySlope_MHz_us"] * 1e+12
        self.idle_time = config["idleTime_us"] * 1e-6
        self.adc_start_time = config["adcStartTime_us"] * 1e-6
        self.ramp_end_time = config["rampEndTime_us"] * 1e-6


class PhaseCalibration:
    """Phase/Frequency calibration.

    Attributes:
        nrx (int): Number of reception antenna
        ntx (int): Number of transmission antenna
        phase (NDarray): Phase calibration matrix
        frequency (NDarray): Frequency calibration matrix
    """

    def __init__(self, filepath: str) -> None:
        """Init Phase/Frequency configuration."""
        with open(os.path.join(ROOTDIR, filepath), "r") as fh:
            config = json.load(fh)
        self.nrx: int = config["nrx"]
        self.ntx: int = config["ntx"]

        # Load phase calibration
        phase_calib_file: str = os.sep.join(
            [*filepath.split("/")[:-1], config["data"]["phase"]]
        )
        phase_calib_file = os.path.join(ROOTDIR, phase_calib_file)
        self.phase = np.fromfile(phase_calib_file, dtype=np.float64, count=-1)
        self.phase = self.phase.reshape(self.ntx, self.nrx, 2)
        self.phase = self.phase[:, :, 0] + 1j * self.phase[:, :, 1]

        # Load frequency calibration
        freq_calib_file: str = os.sep.join(
            [*filepath.split("/")[:-1], config["data"]["frequency"]]
        )
        freq_calib_file = os.path.join(ROOTDIR, freq_calib_file)
        self.frequency = np.fromfile(freq_calib_file, dtype=np.float64, count=-1)
        self.frequency = self.frequency.reshape(self.ntx, self.nrx)


class SCRadarCalibration:
    """Single Chip Radar Calibration.

    Holds the single chip radar sensor calibration parameters

    Attributes:
        antenna: Antenna configuration
        coupling: Antenna coupling calibration
        heatmap: Heatmap recording configuration
        waveform: Waveform generation parameters and calibration
        d: The optimal inter-antenna distance estimation in unit of
           a wavelength
    """

    def __init__(self, config: dict[str, str]) -> None:
        """Init Single Chip radar calibration.

        Arguemnt:
            config: Dictionary containing the paths to files holding the
            radar calibration settiings. The main keys are:

                "antenna": Antenna calibration
                "couling": Coupling calibration
                "heatmap": heatmap configuration
                "waveform": Waveform configuration

            NOTE: See dataset.json
        """
        self.antenna = AntennaConfig(config["antenna"])
        self.coupling = CouplingCalibration(config["coupling"])

    def load_waveform_config(self, descriptor: str) -> None:
        """Load the waveform configuration of a given subset of the dataset.

        Argument:
            descriptor (dict): Contains the global description of the dataset as
                defined in `dataset.json`
        """
        filepath: str = os.path.join(
            descriptor["paths"]["rootdir"],
            descriptor["paths"]["ccradar"]["config"]
        )
        if not os.path.exists(filepath):
            error(f"Waveform configuration file '{filepath}' not found!")
            exit(1)
        self.waveform = WaveformConfiguration(filepath)

        # Chirp start frequency in GHz
        fstart: float = self.waveform.fstart / 1e9
        # Chirp slope in GHz/s
        fslope: float = self.waveform.fslope / 1e9
        # ADC sampling frequency in Hz
        fsample: float = self.waveform.fsample
        # Chrip sampling time in s
        stime: float = self.waveform.ns / fsample
        # Antenna PCB design base frequency
        fdesign: float = self.antenna.fdesign
        self.d = 0.5 * ((fstart + (fslope * stime) / 2) / fdesign)

    def get_coupling_calibration(self) -> np.array:
        """Return the coupling calibration array to apply on the range fft."""
        return self.coupling.data

class CCRadarCalibration(SCRadarCalibration):
    """Cascade Chip Radar Calibration.

    Holds the cascade chip radar sensor calibration parameters

    Attributes:
        antenna: Antenna configuration
        coupling: Antenna coupling calibration
        heatmap: Heatmap recording configuration
        waveform: Waveform generation parameters and calibration
        phase_freq_calib: Phase and frequency calibration
    """

    def __init__(self, config: dict[str, str]) -> None:
        """Init Cascade Chip Radar calibration.

        Argument:
            config: In addition to the keys present in the super class,
            this config add the following one

                "phase": Phase and frequency calibration

        NOTE: See dataset.json
        """
        super(CCRadarCalibration, self).__init__(config)
        self.phase_freq_calib = PhaseCalibration(config["phase"])

    def get_phase_calibration(self) -> np.array:
        """Return the phase calibration array."""
        # Phase calibrationm atrix
        pm = self.phase_freq_calib.phase
        return pm.reshape(
            self.phase_freq_calib.ntx,
            self.phase_freq_calib.nrx,
            1,
            1
        )

    def get_frequency_calibration(self) -> np.array:
        """Return the frequency calibration array."""
        ntx: int = self.phase_freq_calib.ntx
        nrx: int = self.phase_freq_calib.nrx

        fcal_matrix = self.phase_freq_calib.frequency

        fslope: float = self.waveform.fslope
        fsample: float = self.waveform.fsample

        cal_matrix = fcal_matrix * (fslope / fsample)
        cal_matrix /= self.waveform.ns
        cal_matrix = np.expand_dims(cal_matrix, -1) * np.arange(
            self.waveform.ns
        )
        return np.exp(-1j * cal_matrix).reshape( ntx, nrx, 1, self.waveform.ns)


class Calibration:
  """Calibration."""

  def __init__(self, rootdir: dict[str, dict[str, str]]) -> None:
      """Init.

      Argument:
        rootdir: Root directories to access sensors calibration config
      """
      self.ccradar = CCRadarCalibration(rootdir["ccradar"])
