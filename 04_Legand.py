# NOTE The time is saved and then when going back through the stack the final time stays there. 
# NOTE Change Tapping formula 
# NOTE Check if the UI blocks user from scrolling

# @ File(label="Choose folder with TIFF images", style="directory") folder

# Import necessary FIJI/ImageJ and Java modules
from ij import IJ, ImagePlus, ImageStack
from ij.gui import Overlay, TextRoi, GenericDialog
from java.awt import Color, Font
from datetime import datetime
import os, re

# --- Step 1: Get all TIFF files in the selected folder ---
folder_path = folder.getAbsolutePath()
tiff_files = [f for f in sorted(os.listdir(folder_path)) if f.lower().endswith((".tif", ".tiff"))]

if not tiff_files:
    IJ.showMessage("No TIFF images found.")
    exit()

# --- Step 2: Open the first image to extract metadata and dimensions ---
first_path = os.path.join(folder_path, tiff_files[0])
imp_first = IJ.openImage(first_path)
if imp_first is None:
    IJ.showMessage("Could not open first image.")
    exit()

width, height = imp_first.getWidth(), imp_first.getHeight()

# --- Step 3: Try to extract physical scan sizes from TIFF metadata ---
info_str = imp_first.getProperty("Info") or ""
x_scan_length = y_scan_length = None

for line in info_str.splitlines():
    if "32834" in line or "x_scan_length" in line:
        try: x_scan_length = float(line.split("=")[-1].strip())
        except: pass
    if "32835" in line or "y_scan_length" in line:
        try: y_scan_length = float(line.split("=")[-1].strip())
        except: pass

# --- Step 4: Display basic metadata to user ---
msg = "Image size: {} x {} px".format(width, height)
if x_scan_length and y_scan_length:
    px_size_x = x_scan_length / width
    px_size_y = y_scan_length / height
    msg += "\nEstimated Pixel Size:\nX = {:.3e} m/px\nY = {:.3e} m/px".format(px_size_x, px_size_y)
else:
    msg += "\nNo scan size info found in TIFF metadata (tags 32834/32835)."

msg += "\n\nProceeding to manual scale setting..."
IJ.showMessage("TIFF Metadata", msg)

# --- Step 5: Build an image stack from all TIFF files ---
stack = ImageStack(width, height)
for fname in tiff_files:
    imp = IJ.openImage(os.path.join(folder_path, fname))
    if imp is not None:
        stack.addSlice(fname, imp.getProcessor())

if stack.getSize() == 0:
    IJ.showMessage("No valid images loaded.")
    exit()

stack_imp = ImagePlus("Stacked TIFFs", stack)
stack_imp.show()

# --- Apply AFM JPK LUT to the stack ---
IJ.run(stack_imp, "AFM JPK", "")

# --- Step 6: Ask user to set the scale manually (opens dialog) ---
IJ.run("Set Scale...")

# --- Step 7: Metadata parsing helpers ---
def parse_info_param(info, param_name):
    for line in info.split("\n"):
        if param_name in line:
            return line.split(":", 1)[-1].strip()
    return "N/A"

def extract_start_time(info_str):
    match = re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}", info_str)
    if match:
        try:
            dt = datetime.strptime(match.group(), "%Y-%m-%d %H:%M:%S.%f")
            return dt
        except:
            return None
    return None

def get_metadata_values(imp):
    info = imp.getInfoProperty() or ""
    spring = parse_info_param(info, "cantilever-calibration-info.spring-constant")
    sensitivity = parse_info_param(info, "cantilever-calibration-info.sensitivity")
    voltage = parse_info_param(info, "feedback-mode.adjust-reference-amplitude-feedback-settings.reference-amplitude")
    relset = parse_info_param(info, "feedback-mode.setpoint-feedback-settings.relative-setpoint")

    try:
        k = float(spring.split()[0]) / 1000.0  # mN/m → N/m
        s = float(sensitivity.split()[0]) * 1e-9  # nm/V → m/V
        V = float(voltage)
        rel = float(relset)
        F_normal = k * V * s
        F_tapping = k * V * rel
    except:
        F_normal = F_tapping = "N/A"

    return {
        "Title": imp.getTitle(),
        "Time": extract_start_time(info).strftime("%Y-%m-%d %H:%M:%S") if extract_start_time(info) else "N/A",
        "Spring Constant": spring,
        "Normal Force": "{:.2e} N".format(F_normal) if isinstance(F_normal, float) else "N/A",
        "Tapping Force": "{:.2e} N".format(F_tapping) if isinstance(F_tapping, float) else "N/A"
    }

def get_elapsed_times(tiff_paths):
    timestamps = []
    for path in tiff_paths:
        imp = IJ.openImage(path)
        if imp is None:
            timestamps.append(None)
            continue
        info = imp.getInfoProperty() or ""
        dt = extract_start_time(info)
        timestamps.append(dt)

    if not timestamps[0]:
        return [None] * len(timestamps)

    t0 = timestamps[0]
    elapsed = []
    for t in timestamps:
        if t:
            delta = (t - t0).total_seconds()
            elapsed.append(delta)
        else:
            elapsed.append(None)
    return elapsed

# --- Step 8: Ask user which metadata fields to overlay ---
all_params = ["Title", "Time", "Spring Constant", "Normal Force", "Tapping Force", "Elapsed Time"]
gd = GenericDialog("Select Metadata Fields for Overlay")
for p in all_params:
    gd.addCheckbox(p, False)
gd.showDialog()

if gd.wasCanceled():
    exit()

selected = [p for i, p in enumerate(all_params) if gd.getNextBoolean()]
if not selected:
    IJ.showMessage("No parameters selected.")
    exit()

# --- Step 9: Draw overlay text on each slice of the stack ---
image_paths = [os.path.join(folder_path, f) for f in tiff_files]
elapsed_times = get_elapsed_times(image_paths)

font_size = max(10, int(height * 0.03))
spacing = int(font_size * 1.5)
font = Font("SansSerif", Font.PLAIN, font_size)
x, y = 10, 10

for i in range(stack.getSize()):
    imp = IJ.openImage(image_paths[i])
    meta = get_metadata_values(imp)
    overlay = Overlay()
    ypos = y

    for p in selected:
        if p == "Elapsed Time":
            elapsed = elapsed_times[i]
            if elapsed is None:
                value = "N/A"
            elif elapsed < 60:
                value = "{:.3f} s".format(elapsed)
            else:
                minutes = elapsed / 60.0
                value = "{:.2f} min".format(minutes)

        else:
            value = meta.get(p, "N/A")
        text = "{}: {}".format(p, value)
        roi = TextRoi(x, ypos, text, font)
        roi.setStrokeColor(Color.WHITE)
        overlay.add(roi)
        ypos += spacing

    stack_imp.setSlice(i + 1)
    stack_imp.setOverlay(overlay)

stack_imp.updateAndDraw()
