#@ File(label="Choose folder with TIFF images", style="directory") folder

from ij import IJ, ImagePlus, ImageStack
import os

# --- Step 1: Load TIFF images from folder ---
folder_path = folder.getAbsolutePath()
tiff_files = [f for f in sorted(os.listdir(folder_path)) if f.lower().endswith((".tif", ".tiff"))]

if not tiff_files:
    IJ.showMessage("No TIFF images found in selected folder.")
    exit()

# --- Step 2: Open first image to extract metadata ---
first_image_path = os.path.join(folder_path, tiff_files[0])
imp_first = IJ.openImage(first_image_path)

if imp_first is None:
    IJ.showMessage("Could not open first image: " + tiff_files[0])
    exit()

width = imp_first.getWidth()
height = imp_first.getHeight()

# Attempt to read physical scan size from metadata (tags 32834/32835)
info_str = imp_first.getProperty("Info")
x_scan_length = None
y_scan_length = None
if info_str:
    for line in info_str.splitlines():
        if "32834" in line or "x_scan_length" in line:
            try:
                x_scan_length = float(line.split("=")[-1].strip())
            except:
                pass
        if "32835" in line or "y_scan_length" in line:
            try:
                y_scan_length = float(line.split("=")[-1].strip())
            except:
                pass

# --- Step 3: Display metadata info to user ---
msg = "Image dimensions: {} × {} pixels".format(width, height)
if x_scan_length and y_scan_length:
    px_size_x = x_scan_length / width
    px_size_y = y_scan_length / height
    msg += "\n\nEstimated pixel size:\nX = {:.3e} m/pixel\nY = {:.3e} m/pixel".format(px_size_x, px_size_y)
else:
    msg += "\n\nNo physical scan size found in TIFF tags 32834/32835.\nPixel size unknown."

msg += "\n\nYou can now set the scale manually."
IJ.showMessage("TIFF Metadata", msg)

# --- Step 4: Create image stack ---
stack = None
for fname in tiff_files:
    path = os.path.join(folder_path, fname)
    imp = IJ.openImage(path)
    if imp is None:
        IJ.log("Could not open: " + fname)
        continue
    if stack is None:
        stack = ImageStack(imp.getWidth(), imp.getHeight())
    stack.addSlice(fname, imp.getProcessor())

if stack is None or stack.getSize() == 0:
    IJ.showMessage("No valid images to stack.")
    exit()

stack_imp = ImagePlus("Stacked TIFFs", stack)
stack_imp.show()

# --- Step 5: Prompt user to manually set scale ---
IJ.run("Set Scale...")
