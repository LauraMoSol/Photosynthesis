# Manual version of the automated workflow script

# NOTE StagregJ being weird and creating black images 
# NOTE Being improved: Image flattening, Plane leveling
# NOTE This script is fully manual — user interacts with each plugin step

# User manually interacts with each plugin
# Parameters are not predefined
# Log will capture all actions taken by the user

from ij import IJ, WindowManager, ImagePlus, ImageStack
from ij.io import FileSaver
from ij.gui import NonBlockingGenericDialog
from javax.swing import JOptionPane
from ij.plugin import ZProjector
from ij.measure import Calibration
import os

# ========== UTILITY FUNCTIONS ==========

# Dialog that allows user to say Yes or No without blocking ImageJ

def ask_yes_no_nonblocking(title, message):
    gd = NonBlockingGenericDialog(title)
    gd.addMessage(message)
    gd.enableYesNoCancel()
    gd.showDialog()
    return gd.wasOKed()

# Show a preview of the processed image and ask user to accept or reject it

def confirm_step(processed_imp, step_name):
    processed_imp.show()
    confirmed = ask_yes_no_nonblocking("Preview Step: " + step_name,
        "Do you want to accept the result of '{}'?".format(step_name))
    if not confirmed:
        processed_imp.close()
        IJ.log("Step '{}' rejected by user.".format(step_name))
        return False
    return True

# Offer to save the current image with a custom suffix name

def offer_to_save(imp, default_step_name):
    should_save = ask_yes_no_nonblocking("Save Result: " + default_step_name,
        "You accepted '{}'. Save result now?".format(default_step_name))
    if should_save:
        gd = NonBlockingGenericDialog("Name Saved Step")
        gd.addStringField("Filename suffix (no spaces):", default_step_name.replace(" ", "_"))
        gd.showDialog()
        if gd.wasCanceled():
            return False
        custom_name = gd.getNextString().strip().replace(" ", "_")
        fs = FileSaver(imp)
        save_path = os.path.join(folder.getAbsolutePath(), original_title + "_" + custom_name + ".tif")
        fs.saveAsTiff(save_path)
        IJ.log("Saved: " + save_path)
        return True
    else:
        imp.changes = True
        IJ.log("Step '{}' accepted but not saved.".format(default_step_name))
        return False

# Offer to save the ImageJ log as a .txt file

def offer_to_save_log(basename, last_step):
    log = IJ.getLog()
    if not log:
        return
    filename = os.path.join(folder.getAbsolutePath(), basename + "_log_" + last_step.replace(" ", "_") + ".txt")
    with open(filename, 'w') as f:
        f.write(log)
    IJ.log("Log saved to: " + filename)

#@ File(label="Choose folder with TIFF images", style="directory") folder

# ========== IMAGE LOADING ==========

# Load folder of TIFFs
folder_path = folder.getAbsolutePath()
tiff_files = [f for f in sorted(os.listdir(folder_path)) if f.lower().endswith((".tif", ".tiff"))]

if not tiff_files:
    IJ.showMessage("No TIFF images found in selected folder.")
    exit()

# Read metadata from the first image
first_image_path = os.path.join(folder_path, tiff_files[0])
imp_first = IJ.openImage(first_image_path)
if imp_first is None:
    IJ.showMessage("Could not open first image.")
    exit()

original_title = imp_first.getTitle()
width, height = imp_first.getWidth(), imp_first.getHeight()

# Try to extract physical scan size (x/y) from TIFF metadata
info_str = imp_first.getProperty("Info")
x_scan_length = y_scan_length = None
if info_str:
    for line in info_str.splitlines():
        if "32834" in line or "x_scan_length" in line:
            try: x_scan_length = float(line.split("=")[-1].strip())
            except: pass
        if "32835" in line or "y_scan_length" in line:
            try: y_scan_length = float(line.split("=")[-1].strip())
            except: pass

# Show TIFF metadata info to user
msg = "Image dimensions: {} × {} pixels".format(width, height)
if x_scan_length and y_scan_length:
    px_size_x = x_scan_length / width
    px_size_y = y_scan_length / height
    msg += "\n\nEstimated pixel size:\nX = {:.3e} m/pixel\nY = {:.3e} m/pixel".format(px_size_x, px_size_y)
else:
    msg += "\n\nNo physical scan size found in TIFF tags 32834/32835.\nPixel size unknown."
msg += "\n\nYou can now set the scale manually."
IJ.showMessage("TIFF Metadata", msg)

# Stack all images from folder into a single image stack
stack = ImageStack(width, height)
for fname in tiff_files:
    path = os.path.join(folder_path, fname)
    imp = IJ.openImage(path)
    if imp:
        stack.addSlice(fname, imp.getProcessor())

if stack.getSize() == 0:
    IJ.showMessage("No valid images to stack.")
    exit()

# Show the stacked image
imp = ImagePlus("Stacked TIFFs", stack)
imp.show()

# Let user manually set scale
IJ.run("Set Scale...")

# ====== OPTIONAL: Apply LUT for AFM JPK images ======

if ask_yes_no_nonblocking("Apply LUT?", "Do you want to apply the 'AFM JPK' LUT to the stack?"):
    try:
        IJ.selectWindow(imp.getTitle())
        IJ.run("AFM JPK")
        imp = WindowManager.getCurrentImage()
        IJ.log("Applied LUT: AFM JPK and updated image reference.")
    except Exception as e:
        IJ.showMessage("LUT Error", "Failed to apply 'AFM JPK' LUT.\n\n" + str(e))
        IJ.log("LUT application failed: " + str(e))
else:
    IJ.log("User declined LUT application.")

# ========== USER DEFINED WORKFLOW ==========

# Dictionary mapping code numbers to plugin names
step_dict = {
    "1": "Gaussian Blur",
    "2": "Enhance Contrast",
    "3": "Drift Correction",
    "4": "Z Projection",
    "5": "TrackMate Kymograph",
    "6": "Subtract Background"
}

# Prompt user for workflow order
gd = NonBlockingGenericDialog("Workflow Setup")
gd.addMessage(
    "Available Processing Steps:\n"
    "1 = Gaussian Blur\n"
    "2 = Enhance Contrast\n"
    "3 = Drift Correction (StackReg)\n"
    "4 = Z Projection (Best used as FINAL step)\n"
    "5 = TrackMate\n"
    "6 = Subtract Background\n"
    "Note: This version will launch each plugin manually."
)

gd.addStringField("Enter ordered step codes (e.g., 3,1,2,4):", "3,1,2,6,4")
gd.showDialog()

if gd.wasCanceled():
    IJ.showMessage("Aborted", "User cancelled.")
    exit()

# Parse and validate selected steps
step_order = [s.strip() for s in gd.getNextString().split(",") if s.strip() in step_dict]

if not step_order:
    IJ.showMessage("Invalid input", "No valid steps selected.")
    exit()

# ========== EXECUTION ===========

modified = False
final_saved = False

# Process each selected step manually
for idx, step in enumerate(step_order):
    step_label = step_dict[step]
    step_id = "{}_{}".format(step_label.replace(" ", "_"), idx + 1)

    # Duplicate original image for each step
    processed = imp.duplicate()
    processed.show()
    IJ.selectWindow(processed.getTitle())

    # Launch appropriate plugin manually
    if step == "1":
        IJ.run("Gaussian Blur...")
    elif step == "2":
        IJ.run("Enhance Contrast")
    elif step == "3":
        IJ.run("StackReg")
    elif step == "4":
        IJ.run("Z Project...")
        processed = WindowManager.getCurrentImage()
    elif step == "5":
        IJ.run("TrackMate")
    elif step == "6":
        IJ.run("Subtract Background...")

    # Ask user to confirm step result
    if confirm_step(processed, step_id):
        imp.close()
        imp = processed
        modified = True
        final_saved = offer_to_save(imp, step_id)

# ========== FINAL SAVE + LOG ============

if modified:
    if not final_saved and imp.changes:
        offer_to_save(imp, "Final_Result")

    if ask_yes_no_nonblocking("Save Log?", "Save the ImageJ log for this session?"):
        offer_to_save_log(original_title, step_id)

    JOptionPane.showMessageDialog(None,
        "Workflow complete. You may now close the final image if desired.",
        "Done", JOptionPane.INFORMATION_MESSAGE)
else:
    imp.close()
    if ask_yes_no_nonblocking("Save Log?", "No image steps accepted. Still save the log?"):
        offer_to_save_log(original_title, "No_Accepted_Steps")
