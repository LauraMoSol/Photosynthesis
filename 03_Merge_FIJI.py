# NOTE Something is not working but moving on since this goal is less important

#@ File(label="Select first folder with TIFF files", style="directory") folder1
#@ File(label="Select second folder with TIFF files", style="directory") folder2

from ij import IJ, ImagePlus
from ij.io import Opener
from ij.plugin import ImagesToStack
from ij import ImageStack
from java.io import File
from javax.swing import JFrame, JButton
import os

# --- FUNCTION: Return sorted list of TIFFs in a folder ---
def sorted_tiff_paths(folder):
    return sorted([
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.endswith('.tif')
    ])

# --- LOAD TIFFs FROM BOTH FOLDERS ---
folder1_path = folder1.getAbsolutePath()
folder2_path = folder2.getAbsolutePath()

files1 = sorted_tiff_paths(folder1_path)
files2 = sorted_tiff_paths(folder2_path)

if not files1 or not files2:
    IJ.showMessage("Error", "Both folders must contain TIFF files.")
    raise SystemExit

# --- OPEN IMAGES ---
opener = Opener()
images1 = [opener.openImage(f) for f in files1]
images2 = [opener.openImage(f) for f in files2]

# --- CREATE AND DISPLAY STACKS ---
stack1 = ImagesToStack.run(images1)
stack1.setTitle("Stack 1")
stack1.show()
IJ.run(stack1, "Enhance Contrast", "saturated=0.35")

stack2 = ImagesToStack.run(images2)
stack2.setTitle("Stack 2")
stack2.show()
IJ.run(stack2, "Enhance Contrast", "saturated=0.35")

# --- NON-BLOCKING UI WITH BUTTON TO TRIGGER MERGE ---
def merge_stacks(event):
    width = min(stack1.getWidth(), stack2.getWidth())
    height = min(stack1.getHeight(), stack2.getHeight())
    mid = width // 2
    merged_stack = ImageStack(width, height)

    num_slices = min(stack1.getStackSize(), stack2.getStackSize())
    for i in range(num_slices):
        proc1 = stack1.getStack().getProcessor(i + 1).resize(width, height)
        proc2 = stack2.getStack().getProcessor(i + 1).resize(width, height)

        # Debug: check pixel value range
        print("Slice %d Stack1: min=%f, max=%f" % (i+1, proc1.getMin(), proc1.getMax()))
        print("Slice %d Stack2: min=%f, max=%f" % (i+1, proc2.getMin(), proc2.getMax()))

        # Crop and merge
        proc1.setRoi(0, 0, mid, height)
        left = proc1.crop()

        proc2.setRoi(mid, 0, width - mid, height)
        right = proc2.crop()

        left.insert(right, mid, 0)
        merged_stack.addSlice("Merged %d" % (i + 1), left)

    result_imp = ImagePlus("Merged Stack", merged_stack)
    result_imp.show()
    IJ.run(result_imp, "Enhance Contrast", "saturated=0.35")
    frame.dispose()

# --- BUILD MERGE BUTTON UI ---
frame = JFrame("Merge Option")
button = JButton("Merge Halves", actionPerformed=merge_stacks)
frame.add(button)
frame.setSize(200, 100)
frame.setLocationRelativeTo(None)
frame.setVisible(True)
