# Modified: 2023.05.22

import pathlib
import glob
import signal
import queue
import multiprocessing
import threading
import time
import yaml

import os
import time
import pathlib
import numpy as np
import pandas as pd
import tifffile
from skimage.morphology import white_tophat, black_tophat, disk
from skimage import measure, util, morphology, segmentation
from scipy import ndimage
from cellpose import models



# subtract background
def subtract_background(image, radius, light_bg=False):
    # you can also use 'ball' here to get a slightly smoother result at the
    # cost of increased computing time
    str_el = disk(radius)
    if light_bg:
        return black_tophat(image, str_el)
    else:
        return white_tophat(image, str_el)


def image_processing_function(image_loc, config):
    # Read the image into a numpy array of format ZCYX
    img = tifffile.imread(image_loc)
    img_name = pathlib.Path(image_loc).stem
    print(" ")
    print("Processing: ", img_name)

    # - - - - - Nuclear mask
    ## get segmentation channel
    seg_channel = config["segmentation_channel"]
    seg_img = img[:, seg_channel, :, :]

    ## median filter
    median_filter_size = config["median_filter_size"]
    seg_img_median = []
    for z in seg_img:
        seg_img_median_slice = ndimage.median_filter(z, size = median_filter_size)
        seg_img_median.append(seg_img_median_slice)
    seg_img = np.array(seg_img_median)

    ## cellpose parameters
    diameter = config["diameter"]
    flow_threshold = config["flow_threshold"]
    mask_threshold = config["mask_threshold"]
    do_3D = config["do_3D"]
    stitch_threshold = config["stitch_threshold"]
    gpu = config["gpu"]

    ## run cellpose in 3D mode
    model = models.Cellpose(gpu = gpu, model_type = 'cyto')
    masks, flows, styles, diams = model.eval(
        seg_img, 
        channels = [0,0], 
        diameter = diameter, 
        do_3D = do_3D, 
        flow_threshold = flow_threshold, 
        cellprob_threshold = mask_threshold
        )
    
    # - - - - - Dilated nuclear mask 
    ## get expanded masks of each cell labels 
    expansion_px = config["expansion_px"]
    masks_expanded = []
    for z in masks:
        masks_expanded_slice = segmentation.expand_labels(z, distance = expansion_px)
        masks_expanded.append(masks_expanded_slice)
    masks_expanded = np.array(masks_expanded)

    ## get doughnut mask
    masks_doughnut = masks_expanded - masks

    # - - - - - Save mask images

    masks_path = pathlib.Path(config["output_mask_dir"]).joinpath(f"{img_name}_masks.tiff")
    masks_expanded_path = pathlib.Path(config["output_mask_dir"]).joinpath(f"{img_name}_masks_expanded.tiff")
    masks_doughnut_path = pathlib.Path(config["output_mask_dir"]).joinpath(f"{img_name}_masks_doughnut.tiff")

    tifffile.imwrite(masks_path, masks)
    tifffile.imwrite(masks_expanded_path, masks_expanded)
    tifffile.imwrite(masks_doughnut_path, masks_doughnut)
    
    # - - - - - Get nuclei property details
    
    nuc_regionprops = measure.regionprops_table(
    label_image = masks,
    properties = ("label", "area", "centroid", "axis_major_length")
    )

    nuc_df = pd.DataFrame(nuc_regionprops)
    
    # - - - - - Calculate GFP fluorescence intensities
    ## Subtract background
    GFP_channel = config["GFP_channel"]
    bgs_radius = config["bgs_radius"]

    GFP_img = img[:, GFP_channel, :, :]

    GFP_bgs = []
    for z in GFP_img:
        GFP_bgs_slice = subtract_background(z, bgs_radius)
        GFP_bgs.append(GFP_bgs_slice)
    GFP_img = np.array(GFP_bgs)

    ## Measure GFP fluorescence intensity against doughnut mask
    GFP_regionprops = measure.regionprops_table(
        label_image = masks_doughnut,
        intensity_image = GFP_img,
        properties = ("label", "area", "image_intensity")
    )

    GFP_df = pd.DataFrame(GFP_regionprops)
    GFP_df["GFP_intensity_sum"] = GFP_df["image_intensity"].transform(lambda x: np.sum(x))
    GFP_df = GFP_df[["label", "area", "GFP_intensity_sum"]]
    GFP_df = GFP_df.rename(columns={"area":"doughnut_area"})

    # - - - - - Combine nuclear + GFP dataframes
    
    output_df = nuc_df.merge(GFP_df, on = "label", how = "left")
    
    # - - - - - Save output
    
    df_output_path = pathlib.Path(config["output_df_dir"]).joinpath(f"{img_name}_output_df.csv")
    output_df.to_csv(df_output_path)


def worker_function(jobs, results):
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    while not jobs.empty():
        try:
            job = jobs.get(block=False)
            results.put(image_processing_function(*job))
        except queue.Empty:
            pass


def main():
    jobs = multiprocessing.Queue()
    results = multiprocessing.Queue()

    # Load the config file
    with open("analysis-script_batch.yaml") as fi:
        config = yaml.load(fi, Loader=yaml.Loader)

    # Check if output directories exists; try to create them if they don't
    pathlib.Path(config["output_df_dir"]).mkdir(exist_ok=True)
    pathlib.Path(config["output_mask_dir"]).mkdir(exist_ok=True)

    # Fill the job queue either with local files identified using the input path pattern
    image_paths = glob.glob(config["input_pattern"])
    for image_path in image_paths:
        jobs.put((image_path, config))

    # Start workers
    workers = []
    for i in range(config["number_of_workers"]):
        p = multiprocessing.Process(
            target=worker_function, args=(jobs, results)
        )
        p.start()
        workers.append(p)

    # Wait for workers to complete
    try:
        for worker in workers:
            worker.join()
    except KeyboardInterrupt:
        for worker in workers:
            worker.terminate()
            worker.join()


if __name__ == "__main__":
    # Set the process start method; spawn is default on Windows
    multiprocessing.set_start_method("spawn")
    # Call the main function
    main()
    print(" ")
    print("Batch process done!! XD")
