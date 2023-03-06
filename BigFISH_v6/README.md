# Big-FISH smFISH spot quantification scripts

Pre-process and quantify single-molecule Fluorescence in situ Hybridisation images using a python package Big-FISH: https://github.com/fish-quant/big-fish.
Measure (1) individual spot counts in the cell + (2) spot counts within signal dense regions.

## Installation

### Set up virtual conda environment 

Make sure to use x86 version of Miniconda3, not the arm64 version (even if using M1 mac computers): https://docs.conda.io/en/latest/miniconda.html

    conda create -n bigfish_v6 python=3.7
    conda activate bigfish_v6

    # virtual environment can be detactivated as follows
    conda deactivate

### BigFISH installation

    pip install big-fish
    pip install ipykernel
    pip install jupyterlab

    pip install cellpose # if segmenting tissue culture cells

## smFISH quantification

### Optimise parameters 

Use `smFISH-quantification_optimise-parameters.ipynb` notebook to determine smFISH quantification parameters. Also determine if you will be using manual intensity threshold or automatic thresholding. 

Use `jupyterlab` to open the optimise-parameters notebook

    jupyterlab


### Batch processing 

TBC..

