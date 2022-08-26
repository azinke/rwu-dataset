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
        num_rx (int): Number of reception antenna
        num_tx (int): Number of transmission antenna
        num_range_bins (int): Number of range bins
        num_doppler_bins (int): Number of doppler frequency bins
        data (list[float]): Array description coupling calibartion data

    TODO: Process rge raw calibration data
    """

    def __init__(self, filepath: str) -> None:
        """Init coupling calibration."""
        with open(os.path.join(ROOTDIR, filepath), "r") as fh:
            # TODO: Load coupling calibration matrix
            pass


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
        num_rx (int): Number of reception antenna
        num_tx (int): Number of transmission antenna
        frequency_slope (float): Frequency slope
        sampling_rate (float): ADC sampling frequency in Herz
        frequency_calibration_matrix (list[float]): Sensor frequency
        calibration matrix
    """

    def __init__(self, filepath: str) -> None:
        """Init Phase/Frequency configuration."""
        with open(os.path.join(ROOTDIR, filepath), "r") as fh:
            # Load Phase/Amplitude calibration file
            pass


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
        # self.coupling = CouplingCalibration(config["coupling"])

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
        return np.array(self.coupling.data).reshape(
            self.coupling.num_tx,
            self.coupling.num_rx,
            1,
            self.waveform.num_adc_samples_per_chirp,
        )


class CCRadarCalibration(SCRadarCalibration):
    """Cascade Chip Radar Calibration.

    Holds the cascade chip radar sensor calibration parameters

    Attributes:
        antenna: Antenna configuration
        coupling: Antenna coupling calibration
        heatmap: Heatmap recording configuration
        waveform: Waveform generation parameters and calibration
        phase: Phase and frequency calibration
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
        # self.phase = PhaseCalibration(config["phase"])

    def get_phase_calibration(self) -> np.array:
        """Return the phase calibration array."""
        # Phase calibrationm atrix
        pm = np.array(self.phase.phase_calibration_matrix)
        pm = pm[::2] + 1j * pm[1::2]
        pm = pm[0] / pm
        return pm.reshape(
            self.phase.num_tx,
            self.phase.num_rx,
            1,
            1
        )

    def get_frequency_calibration(self) -> np.array:
        """Return the frequency calibration array."""
        num_tx: int = self.phase.num_tx
        num_rx: int = self.phase.num_rx

        # Calibration frequency slope
        fcal_slope: float = self.phase.frequency_slope
        # Calibration sampling rate
        cal_srate: int = self.phase.sampling_rate

        fcal_matrix = np.array(self.phase.frequency_calibration_matrix)

        fslope: float = self.waveform.frequency_slope
        srate: int = self.waveform.adc_sample_frequency

        # Delta P
        # 
        dp = fcal_matrix - fcal_matrix[0]

        cal_matrix = 2 * np.pi * dp * (fslope / fcal_slope) * (cal_srate / srate)
        cal_matrix /= self.waveform.num_adc_samples_per_chirp
        cal_matrix.reshape(num_tx, num_rx)
        cal_matrix = np.expand_dims(cal_matrix, -1) * np.arange(
            self.waveform.num_adc_samples_per_chirp
        )
        return np.exp(-1j * cal_matrix).reshape(
            num_tx,
            num_rx,
            1,
            self.waveform.num_adc_samples_per_chirp
        )


class Calibration:
  """Calibration."""

  def __init__(self, rootdir: dict[str, dict[str, str]]) -> None:
      """Init.

      Argument:
        rootdir: Root directories to access sensors calibration config
      """
      self.ccradar = CCRadarCalibration(rootdir["ccradar"])
