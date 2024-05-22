# Welcome to the Xdas tutorial series!

[![DOI](https://zenodo.org/badge/802170309.svg)](https://zenodo.org/badge/latestdoi/802170309)

This repository contains a series of tutorials to learn and play with the [Xdas](https://github.com/xdas-dev/xdas) python library. Xdas is a Python library designed to facilitate the processing and analysis of DAS data.

## Overview

This tutorial series aims to provide a comprehensive guide to using the Xdas library, from basic data manipulation to advanced analysis techniques.

You first need to setup an working environment. Then the tutorials are organized in a progressive manner, with each tutorial building on concepts introduced in the previous ones. It's recommended to go through them in order.

## Setup the tutorial environment

### Get the source code

Clone it from this repository:

```
git clone https://github.com/xdas-dev/tutorials.git
cd tutorials
```

To reset the folder to initial state you can do:

```
git reset --hard HEAD
```

You can also fetch latest updates by:

```
git pull
```

### Creating a dedicated environment

We  recommend to use conda to create an isolated environment:

```
conda config --add channels conda-forge
conda create -n xdas-tutorials
conda activate xdas-tutorials
conda install pip --yes
```

### Installing Xdas

Xdas is a pure python package. It can easily be installed with pip from PyPI:

```
pip install xdas
```

### Additional dependencies

This series of tutorials also require additional libraries

```
pip install notebook seisbench
```

### Download Data samples

Some samples are gracefully provided by the ABYSS project. You can download them from zenodo:

```
wget https://zenodo.org/records/11212055/files/data.zip
unzip data.zip
rm -rf outputs
mkdir -p outputs
```

You are ready to go!