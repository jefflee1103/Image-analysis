// For use with MK's fishquant_outline.py script
// Use Max projected images to draw ROIs adding them to ROI manager
// Run this macro to export imagej ROI to "filename.tif.zip" in the same directory as the MAX image

outDir = getDirectory("image");
name = getTitle;
path = outDir+name

roiManager("Save", path+".zip");
