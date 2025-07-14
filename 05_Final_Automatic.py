# NOTE StagregJ being weird and creating black images 
# NOTE Being imporved: Image flattening, Plane leveling
# NOTE Script is automatic 

from ij import IJ, WindowManager, ImagePlus, ImageStack
from ij.io import FileSaver
from ij.gui import NonBlockingGenericDialog
from javax.swing import JOptionPane
from ij.plugin import ZProjector
from ij.measure import Calibration
import os

# ========== UTILITY FUNCTIONS ==========

def ask_yes_no_nonblocking(title, message):
    gd = NonBlockingGenericDialog(title)
    gd.addMessage(message)
    gd.enableYesNoCancel()
    gd.showDialog()
    return gd.wasOKed()

def confirm_step(processed_imp, step_name):
    processed_imp.show()
    confirmed = ask_yes_no_nonblocking("Preview Step: " + step_name,
        "Do you want to accept the result of '{}'?".format(step_name))
    if not confirmed:
        processed_imp.close()
        IJ.log("Step '{}' rejected by user.".format(step_name))
        return False
    return True

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

def offer_to_save_log(basename, last_step):
    log = IJ.getLog()
    if not log:
        return
    filename = os.path.join(folder.getAbsolutePath(), basename + "_log_" + last_step.replace(" ", "_") + ".txt")
    with open(filename, 'w') as f:
        f.write(log)
    IJ.log("Log saved to: " + filename)

def process_stack_slices(imp, step_name, command, args):
    stack = imp.getStack()
    new_stack = ImageStack(stack.getWidth(), stack.getHeight())
    for i in range(1, stack.getSize() + 1):
        imp.setSlice(i)
        IJ.run(imp, command, args)
        new_stack.addSlice(stack.getSliceLabel(i), imp.getProcessor().duplicate())
    return ImagePlus(imp.getTitle() + " - " + step_name, new_stack)

#@ File(label="Choose folder with TIFF images", style="directory") folder

# ========== IMAGE LOADING ==========
folder_path = folder.getAbsolutePath()
tiff_files = [f for f in sorted(os.listdir(folder_path)) if f.lower().endswith((".tif", ".tiff"))]

if not tiff_files:
    IJ.showMessage("No TIFF images found in selected folder.")
    exit()

first_image_path = os.path.join(folder_path, tiff_files[0])
imp_first = IJ.openImage(first_image_path)
if imp_first is None:
    IJ.showMessage("Could not open first image.")
    exit()

original_title = imp_first.getTitle()
width, height = imp_first.getWidth(), imp_first.getHeight()

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

msg = "Image dimensions: {} × {} pixels".format(width, height)
if x_scan_length and y_scan_length:
    px_size_x = x_scan_length / width
    px_size_y = y_scan_length / height
    msg += "\n\nEstimated pixel size:\nX = {:.3e} m/pixel\nY = {:.3e} m/pixel".format(px_size_x, px_size_y)
else:
    msg += "\n\nNo physical scan size found in TIFF tags 32834/32835.\nPixel size unknown."
msg += "\n\nYou can now set the scale manually."
IJ.showMessage("TIFF Metadata", msg)

stack = ImageStack(width, height)
for fname in tiff_files:
    path = os.path.join(folder_path, fname)
    imp = IJ.openImage(path)
    if imp:
        stack.addSlice(fname, imp.getProcessor())

if stack.getSize() == 0:
    IJ.showMessage("No valid images to stack.")
    exit()

imp = ImagePlus("Stacked TIFFs", stack)
imp.show()

IJ.run("Set Scale...")

# ====== OPTIONAL: Apply AFM JPK LUT ======
if ask_yes_no_nonblocking("Apply LUT?", "Do you want to apply the 'AFM JPK' LUT to the stack?"):
    try:
        IJ.selectWindow(imp.getTitle())
        IJ.run("AFM JPK")

        # Re-acquire the modified stack from the window (to ensure LUT is attached)
        imp = WindowManager.getCurrentImage()
        IJ.log("Applied LUT: AFM JPK and updated image reference.")
    except Exception as e:
        IJ.showMessage("LUT Error", "Failed to apply 'AFM JPK' LUT.\n\n" + str(e))
        IJ.log("LUT application failed: " + str(e))
else:
    IJ.log("User declined LUT application.")

# ========== USER DEFINED WORKFLOW ==========

step_dict = {
    "1": "Gaussian Blur",
    "2": "Enhance Contrast",
    "3": "Drift Correction",
    "4": "Z Projection",
    "5": "TrackMate Kymograph",
    "6": "Subtract Background"
}

gd = NonBlockingGenericDialog("Workflow Setup")
gd.addMessage(
    "Available Processing Steps:\n"
    "1 = Gaussian Blur\n"
    "2 = Enhance Contrast\n"
    "3 = Drift Correction (StackReg)\n"
    "4 = Z Projection (Best used as FINAL step)\n"
    "5 = TrackMate\n"
    "6 = Subtract Background\n"
    "Note: You can apply multiple steps in any order."
)

gd.addStringField("Enter ordered step codes (e.g., 3,1,2,4):", "3,1,2,6,4")
gd.addStringField("Parameters (semicolon-separated for steps 1–6):", "sigma=2; saturated=0.35; ; ; ; rolling=50")

gd.showDialog()

if gd.wasCanceled():
    IJ.showMessage("Aborted", "User cancelled.")
    exit()

step_order = [s.strip() for s in gd.getNextString().split(",") if s.strip() in step_dict]
param_list = [s.strip() for s in gd.getNextString().split(";")]

if not step_order:
    IJ.showMessage("Invalid input", "No valid steps selected.")
    exit()

# ========== PREVIEW WORKFLOW ==========

preview = "Selected Workflow:\n\n"
for i, step in enumerate(step_order):
    label = step_dict[step]
    params = param_list[int(step) - 1] if int(step) - 1 < len(param_list) else ""
    preview += "{}. {} ({})\n".format(i + 1, label, params or "default")
ask_continue = ask_yes_no_nonblocking("Workflow Confirmation", preview + "\n\nProceed with this workflow?")
if not ask_continue:
    exit()

# ========== EXECUTION ==========

modified = False
final_saved = False

for idx, step in enumerate(step_order):
    step_label = step_dict[step]
    step_id = "{}_{}".format(step_label.replace(" ", "_"), idx + 1)
    param = param_list[int(step) - 1] if int(step) - 1 < len(param_list) else ""

    if step == "1":
        processed = process_stack_slices(imp, step_label, "Gaussian Blur...", param or "sigma=2")
    elif step == "2":
        processed = process_stack_slices(imp, step_label, "Enhance Contrast", param or "saturated=0.35")

    elif step == "3":
        processed = imp.duplicate()
        processed.show()
        IJ.selectWindow(processed.getTitle())

        # Ask user for the reference slice
        slice_gd = NonBlockingGenericDialog("StackReg Reference Slice")
        slice_gd.addNumericField("Select reference slice (1 - {}):".format(processed.getStackSize()), 1, 0)
        slice_gd.showDialog()

        if slice_gd.wasCanceled():
            IJ.log("User cancelled reference slice selection.")
            processed.close()
            continue

        ref_slice = int(slice_gd.getNextNumber())
        if ref_slice < 1 or ref_slice > processed.getStackSize():
            IJ.showMessage("Invalid Slice", "Reference slice out of range.")
            processed.close()
            continue

        processed.setSlice(ref_slice)
        IJ.run("StackReg ")
        processed = WindowManager.getCurrentImage()

    elif step == "4":
        projection_source = imp.duplicate()
        projector = ZProjector(projection_source)
        projector.setMethod(ZProjector.AVG_METHOD)
        projector.doProjection()
        processed = projector.getProjection()
        projection_source.close()
    elif step == "5":
        processed = imp.duplicate()
        processed.show()
        IJ.selectWindow(processed.getTitle())
        IJ.run("TrackMate")
        confirmed = ask_yes_no_nonblocking("TrackMate Kymograph",
            "TrackMate has launched.\n\nPlease use the KymographBuilder extension inside TrackMate.\n\nClick OK when finished.")
        if not confirmed:
            processed.close()
            continue
        processed = WindowManager.getCurrentImage()
    elif step == "6":
        processed = process_stack_slices(imp, step_label, "Subtract Background...", param or "rolling=50")

    if confirm_step(processed, step_id):
        imp.close()
        imp = processed
        modified = True
        final_saved = offer_to_save(imp, step_id)

# ========== FINAL SAVE + LOG ==========

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
