// ImageJ Macro: Batch process TIFF files in a directory
// Prompts user for directory and channel, processes each TIFF file

dir = getDirectory("Choose a directory with TIFF files");
if (dir == null) exit("No directory selected.");

pdf_channel = getNumber("Enter channel number for pdf_channel (1-based):", 1);

list = getFileList(dir);
for (i = 0; i < list.length; i++) {
	if (endsWith(list[i], ".tif") || endsWith(list[i], ".tiff")) {
		open(dir + list[i]);
		run("Split Channels");
		selectWindow("C" + pdf_channel);
		run("Subtract Background...", "rolling=50");
		run("Median...", "radius=2");
		// Optionally, save the result
		// saveAs("Tiff", dir + "processed_" + list[i]);
		close();
	}
}
