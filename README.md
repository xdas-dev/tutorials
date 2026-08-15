# Welcome to the Xdas tutorial series!

[![DOI](https://zenodo.org/badge/802170309.svg)](https://zenodo.org/badge/latestdoi/802170309)

This repository contains a series of tutorials to learn and play with the [Xdas](https://github.com/xdas-dev/xdas) python library. Xdas is a Python library designed to facilitate the processing and analysis of DAS data.

## Overview

This tutorial series aims to provide a comprehensive guide to using the Xdas library, from basic data manipulation to advanced analysis techniques.

You first need to setup an working environment. Then the tutorials are organized in a progressive manner, with each tutorial building on concepts introduced in the previous ones. It's recommended to go through them in order.

| Notebook | What it covers |
|---|---|
| [01](01_open_and_consolidate.ipynb) | Linking thousands of files into one virtual array, and gathering several cables into one tree |
| [02](02_exploration&processing.ipynb) | Selecting, plotting and processing in physical units |
| [03](03_massive_atomic_processing.ipynb) | Atoms: chunked processing that gives the same answer as a single pass |
| [04](04_playing_with_coordinates.ipynb) | Coordinates: repairing timing that lies, cable geometry, channel names, swapping dimensions |
| [05](05_seismological_stations.ipynb) | The same pipeline on a regional seismological network, fetched from FDSN |
| [06](06_catalog_with_gamma.ipynb) | Associating and locating with GaMMA to build a small catalog |
| [07](07_manual_picking_with_xpick.ipynb) | Reviewing and correcting picks by hand with xpick |

The data is a set of telecom cables interrogated in central Chile during the
POST and ABYSS experiments; the earthquake used from notebook 02 onwards is a
real one, offshore Coquimbo.

## Setup the tutorial environment

Everything is done by one command. It needs [uv](https://docs.astral.sh/uv/),
which installs itself in one line too:

```
curl -LsSf https://astral.sh/uv/install.sh | sh    # macOS and Linux
```

Then clone the tutorials and run the installer:

```
git clone https://github.com/xdas-dev/tutorials.git
cd tutorials
uv run install.py
```

That single command creates the environment, installs every library the seven
notebooks use, downloads the DAS samples from Zenodo and unzips them into
`data/`, and fetches the seismological waveforms of notebook 05 into
`data/stations/` — one miniSEED file per station, plus the inventory.

A few things worth knowing before you start it:

- **It downloads 3.6 GB and unpacks to 4.5 GB**, so keep ~9 GB free while it
  runs. The archive is deleted once unzipped.
- **It is safe to re-run.** A step already done is skipped, and an interrupted
  download resumes where it stopped. Use `uv run install.py --force` to fetch
  everything again from scratch.
- **Notebook 07 additionally needs Node.js** on your `PATH`: xpick serves a
  Bokeh app whose picker tool is compiled when it starts. Any recent Node.js
  will do, for instance `conda install "nodejs>=18"`.

Then start Jupyter — no environment to activate, `uv run` uses the right one:

```
uv run jupyter lab
```

The samples are gracefully provided by the ABYSS project and hosted
[on Zenodo](https://zenodo.org/records/11212055); the station waveforms come
from the EarthScope FDSN service.

### Keeping up to date

To fetch the latest version of the tutorials:

```
git pull
```

To reset the folder to its initial state (this does not touch `data/`):

```
git reset --hard HEAD
```

### A note on the network

Once `install.py` has run, the only thing still downloaded at run time is the
`seisbench` pretrained model, fetched the first time notebook 03 picks — so
run notebook 03 once while connected. Everything else is on disk.

You are ready to go!