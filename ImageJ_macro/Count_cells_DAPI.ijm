// Define input and output directories
input = getDirectory("Choose Source Directory ");
output = getDirectory("Choose Destination Directory ");

// Open files
list = getFileList(input);

setBatchMode(true);

for (i=0; i<list.length; i++) {
	showProgress(i+1, list.length);
	path = input + list[i];
	open(path);
	fileName = substring(list[i],0,lengthOf(list[i])-4);
	run("Z Project...", "projection=[Max Intensity]");
	run("Subtract Background...", "rolling=200");
	run("Median...", "radius=10");
	setAutoThreshold("Huang dark");
	run("Convert to Mask");
	run("Dilate");
	run("Fill Holes");
	run("Watershed");
	run("Analyze Particles...", "size=50.00-Infinity circularity=0.50-1.00 display clear summarize");
	run("Close All");
}

selectWindow("Summary");
saveAs("Results", output+"DAPI_count_output.csv");
	
	

