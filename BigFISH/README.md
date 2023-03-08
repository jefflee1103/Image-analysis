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

    # if segmenting tissue culture cells also install cellpose (the version may need to be 0.7.2)
    pip install cellpose 

## smFISH quantification

### Optimise parameters 

Use `smFISH-quantification_optimise-parameters.ipynb` notebook to determine smFISH quantification parameters on a few subset of images.

    cd /path/to/working/directory/
    jupyter lab

Following should be determined from the notebook:

* Image voxel size and PSF parameters
* Image channels to quantify (0-based)
* Whether auto thresholding will be used 
    * requires a fair number of spots within the image
    * signal-to-background ratio of smFISH spots should be > 2 in raw images for reliable use
* If not using automated thresholding, find a suitable manual intensity threshold 
    * Draw several line profiles over smFISH spots in `rna_log.tif` on ImageJ to find a suitable threshold
* Dense region decomposition parameters
    * how wide the dense regions should be? (`bf_radius` in nanometers)
    * minimum number of spots within a dense region for it to be considered a cluster (`nb_min_spots`)

### Batch processing multiple images 

Port the pre-determined quantification parameters to `smFISH_analysis_config.yaml` file. 

#### General configuration 

* `number_of_workers`: Number of CPUs to use
* `input_pattern`: Input image directory - use wildcard to grab the images 
* `output_dir`: Directory where spot and cluster coordinates will be saved 
* `output_qc_dir`: Directory where quality control files will be saved (e.g. reference spot, elbow plot..etc)

#### Bigfish configuration

* `voxel_size_yx`: XY voxel size in nm
* `voxel_size_z`: Z step voxel size in nm
* `ex`: Dye excitation maxima
* `em`: Dye emission maxima
* `NA`: Numerical aperture of the microscope objective
* `RI`: Refractive index of the mounting media
* `microscope`: Either 'confocal' or 'widefield'

* `bg_radius`: Background subtraction kernel radius. Usually 5 is okay. 

* `channels`: Image channels to quantify (0-based). Use [2, 3] or [2] format 

* `auto_threshold`: True/False - Whether automated thresholding will be used

* `smFISH_ch1`: First smFISH channel number - should match the `channels` configuration 
* `smFISH_ch1_thresh`: LoG filtered spot intensity threshold for the first channel 
* `smFISH_ch2`: Second smFISH channel number 
* `smFISH_ch2_thresh`: LoG filtered spot intensity threshold for the second channel 

* `alpha`: 0.5 - Do not change 
* `beta`: 1 - Do not change 
* `bf_radius`: Cluster radius in nanometer
* `nb_min_spots`: Mimimum number of spots required for a dense region to be considered a cluster. 


#### Start batch process

Start the batch process by running the multiprocess python script. Make sure the YAML configuration file is in the same directory as the python script. 

    cd /path/to/python/script/
    python smFISH_data_analysis_multiprocess.py


