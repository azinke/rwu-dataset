# RWU-Dataset

This tool allows you to access and post-process the recordings of the `RWU-Dataset`. It only hosts
currently recordings of the cascaded RADAR but can be easily extended to other sensors (Camera,
Lidar, IMU, etc.).

The Radar dataset contains the raw ADC samples of the cascaded MMWCAS-RF evaluation module of Texas
Instruments.

## Environment setup

**Note**: *At least python `3.10` is needed to setup this tool for usage.*

Create a python virtual environment and install the required packages as follows

```bash
python -m venv venv
source ./venv/bin/activate

python -m pip install -r requirements.txt
```

## RWU dataset

**TODO**: *Add the link to download the dataset*

## Setup and configuration

The structure of this repository is as follows

```txt
.
├── core
├── dataset
│   ├── calibration
│   │   └── cascade
│   │       ├── antenna_cfg.json
│   │       ├── coupling_calibration.bin
│   │       ├── coupling_cfg.json
│   │       ├── frequency_calibration.bin
│   │       ├── phase_amp_calibration.bin
│   │       └── waveform_calib_cfg.json
│   └── dataset.json
├── __init__.py
├── rwu.py
├── README.md
└── requirements.txt
```

The folder `calibration/cascade` holds the calibration data of the cascaded radar sensor. The recordings
must be downloaded and unzipped in the `dataset` folder. Then, the folder structure would look like this:

```txt
.
├── core
├── dataset
│   ├── parking-05092200
│   ├── parking-05092201
│   ├── parking-05092202
│   ├── parking-05092203
│   ├── parking-05092204
│   ├── room-02092200
│   ├── room-05092201
│   └── room-05092202
│   ├── calibration
│   └── dataset.json
├── __init__.py
├── rwu.py
├── README.md
└── requirements.txt
```

The naming convention used for the folders containing recordings is `<name>-<dd-mm-yy><nn>`. With
`<name>` a name describing the scene or the place of the recording, `<dd-mm-yy>` a 2-digit date format
 (`d`: day, `m`: month, `y`: year) and `<nn>` a 2-digit order number.

In the snippet above, one can notice that multiple subset of the dataset are present in the `dataset`fodler.
The key point to configure the supported subset of the dataset and how to access them is the
`dataset/dataset.json` file.

The only part that requires your attention is the `folders` key of the `datastore` entry.

```json
    "folders": [
      {
        "codename": "parking0",
        "path": "parking-05092200"
      },
      {
        "codename": "parking1",
        "path": "parking-05092201"
      },
      {
        "codename": "parking2",
        "path": "parking-05092202"
      },
      {
        "codename": "parking3",
        "path": "parking-05092203"
      },
      {
        "codename": "parking4",
        "path": "parking-05092204"
      },
      {
        "codename": "room0",
        "path": "room-05092200"
      },
      {
        "codename": "room1",
        "path": "room-05092201"
      },
      {
        "codename": "room2",
        "path": "room-05092202"
      }
    ]
```

 In the example shown above, each subset of the dataset to handle, is registered along with a short
`codename` to access it. The subset already mentioned can be accessed with their corresponding
codename. New subsets of the dataset can be added similarly. The codenames can even be updated to
suit the naming convention that you would prefer. With that, you're all set to play around with the
dataset.

## Usage

**IMPORTANT NOTE**:
- _If you've setted up a virtual environment, don't forget to enable it first_
- _Rendering are done based on a web based backend. So, a web browser tab will automatically be launched for all renderings._

The easiest way to have an overview of all the available options to interact with the datatset
is the help command.


```bash
python rwu.py -h
```

However, find below the cheat-sheet of this CLI tool


1. Overview

```bash
# Print the 'dataset.json' configuration file
python rwu.py -o
python rwu.py --overview
```

Either one of this command pretty print the entire `dataset/dataset.json` file to allow a quick
overview of the current configuration in use.

Since each subset of the dataset receives a codename to interact with it, you can request
the list of currently registered subsets of the dataset and their codenames as follow:

```bash
# Get the list of registered dataset and their codenames
python rwu.py -o --codename
python rwu.py --overview --codename
```

2. Radar sensor

The shorthand used to access the cascaded chip radar data is `ccradar`. Therefore, we have the
following commands

```bash
#
# Processing or raw ADC samples
#

# Render cascaded chip radar  4D heatmap  from raw ADC samples (in polar coordinate)
# --min-range allows to skip very close range pointclouds that are not often coherent
python rwu.py --dataset <codename> -i <frame-index> --ccradar --raw --polar [--min-range <range>]

# Render cascaded chip radar  3D heatmap  from raw ADC samples (in cartesian coordinate)
python rwu.py --dataset <codename> -i <frame-index> --ccradar --raw [--min-range <range>]

# To render the heatmap with velocity as the fourth dimension, use the `--velocity-view` argument
python rwu.py --dataset <codename> -i <frame-index> --ccradar --raw --velocity-view

# The threshold for filtering the heatmap can be adjusted with `--threshold`. The value
# of the threshold is expected to be in the interval [0; 1]
python rwu.py --dataset <codename> -i <frame-index> --ccradar --raw --threshold <value>


# Render cascaded chip radar  2D heatmap  from raw ADC samples
python rwu.py --dataset <codename> -i <frame-index> --ccradar --raw --heatmap-2d

# Render cascaded chip radar  3D pointcloud  from raw ADC samples
python rwu.py --dataset <codename> -i <frame-index> --ccradar --raw --pcl

# Render cascaded chip radar pointcloud bird eye view  from raw ADC samples
python rwu.py --dataset <codename> -i <frame-index> --ccradar --raw --pcl -bev
```

See examples below:

```bash

# Render cascaded radar 3D heatmap skiping the first 1.5m range
python rwu.py --dataset parking1 -i 130 --ccradar --raw --min-range 1.5

# Render cascaded radar 3D heatmap skiping the first 1.5m range, with velocity as the fourth dimension
python rwu.py --dataset parking2 -i 498 --ccradar --raw --polar --min-range 1.5 --velocity-view

# Render cascaded radar 3D heatmap with a threshold value of 0.4
python rwu.py --dataset parking1 -i 65 --ccradar --raw --min-range 1.5 --threshold 0.4

# Render cascaded chip radar pointcloud bird eye view from raw ADC samples
python rwu.py --dataset parking4 -i 175 --ccradar --raw -pcl -bev
```

3. Batched processing and save output

You can note that the index option `-i` is no longer needed. The path given for
the `save-to` option could be a non-existing one. The path will automatically be
created in that case.

```bash
# Render and save all cascaded chip radar plointcloud bird eye view of a given subset of the dataset
python rwu.py --dataset <codename> --ccradar --raw -pcl -bev --save-to <output-directory>
```

4. Animation

```bash
# Create a video out of the images present in the input folder provided
python rwu.py --dataset <codename> --animate <path-to-image-folder>
```

The generated video is saved in the same folder as the images.
