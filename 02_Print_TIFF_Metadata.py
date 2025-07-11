import os              # For file operations
import tifffile        # For reading TIFF files and metadata
import tkinter as tk   # For folder selection UI
from tkinter import filedialog

# --- Prompt user to select the folder containing TIFF files ---
root = tk.Tk()
root.withdraw()  # Hide the empty root window
tiff_folder = filedialog.askdirectory(title="Select Folder Containing TIFF Files")
if not tiff_folder:
    raise SystemExit("No folder selected. Exiting.")

# --- Loop through all .tif files in the folder, sorted alphabetically ---
for filename in sorted(os.listdir(tiff_folder)):
    if filename.endswith(".tif"):
        path = os.path.join(tiff_folder, filename)

        # --- Open the TIFF file and read the ImageDescription tag from the first page ---
        with tifffile.TiffFile(path) as tif:
            desc = tif.pages[0].tags.get("ImageDescription")

            # --- Print the metadata or a message if it's missing ---
            print(f"\n=== {filename} ===")
            print(desc.value if desc else "No metadata found.")
