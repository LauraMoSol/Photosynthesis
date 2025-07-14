# Photosynthesis
                                                                                                 
                                                 ▓█                                                 
                                       ▓▓        ▓█        ▓                                        
                                         ▓▓      ▓█      █▓                                         
                                          █▓            ▓▓                                          
                                                                                                    
                                                 █▓▓▓                                               
                                 ▓▓▓▓█        █▓▓▓▓▓▓                                               
                                 █▓▓▓▓▓▓▓    ▓▓▓░▓▓▓                                                
                                  ▓▓▓▓░▓▓▓░ █▓▓▓▓▓▓░         ▓██████                                
                                   ▓▓▓▓▓░█▓ ▓██▓▓█         ░▓▓▓▓▓▓▓▓▓▓                              
                           ▒▓▓▓▓▓▓█  ░▓▓▓▓▓ █▓█    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░                           
                         ▓▓█░             ▓▓▓                          ▒▓▓█                         
                        ▓▓                 ▓▓                             ▓▓                        
                       ▓▓░                  ▓   ▓▓▓▓█           ░▓▓▓▓▓█   █▓                        
                       █▓                   ▓ █▓▓▓▓▓            ▓▓▓▓▓▓▓   █▓░                       
                       ▓▓                 ▓▓▓▓▓▓▓▓▓░▓▓█         ▓▓▓▓▓▓▓   █▓░                       
                       ▓▓               ▓▓   ▓▒       ▓▓█                 █▓░                       
                       █▓             ░▓█     ▓         ▓█                █▓░                       
                       █▓             ▓█       ▓         ▓▓               █▓░                       
                       █▓            ░▓░       ▓▒ ░▓▓▓▒  ▓▓               █▓░                       
                       ▓▓            ░▓   ▓▓▓█ ▒▒▓▓▓▓▒   ▓▓               █▓░                       
                       ▓▓             ▓█   ▓▓▓▓▒▓▓█░     ▓█               █▓░                       
                       ▓▓             ▒▓▓     ░▓▒       ▓▓                █▓░                       
                       █▓               ▓▓     ▓      ▒▓▓                 █▓░                       
                       █▓                ▒▓▓▓ ▒▓   ░▓▓▓                   █▓░                       
                       ▓▓                   ░█▓▓▓▓▓▓                      █▓░                       
                        ▓█                                                ▓▓                        
                         ▓▓▒                                            ▓▓▓                         
                           ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                           
                                                                                                    
                                                                                                    
                                                                                                    
      ░▓██▓▓▒ ▓              ▓                                ▓   ▓▓                  ██            
      ░▓   ██ ▓░▓▓█   █▓▓▓ ░▓▓▓▓  ▓▓▓█   ▓▓▓▓ ▓▒   ▓░░▓░▓▓█ ░▓▓▓▓ ▓▓▓▓▓░  █▓▓▓   █▓▓█ ▒▓  ▓▓▓█      
      ░▓▓▓▓▓░ ▓   ▓█ ▓▒   ▓  ▓   ▓   ░▓ █▓░    ▓  ▓█ ░▓   ▓▒  ▓   ▓▒  █▓ ▓█   ▓ ░▓▒   ▒▓ █▓▒        
      ░▓      ▓   ▓█ ▓▒  ░▓  ▓   ▓░  ▒▓    ▒▓  ▓▓▓▓  ░▓   ▓▒  ▓   ▓▓  ▓▓ ▓█         ▓░▒▓    ░▓      
      ░▓      ▓   ▓█  █▓▓█   █▓▓  █▓▓█  ░▓▓▓▓   ▓▓   ░▓   ▓░  █▓▓ ▓▓  ▓▓  ▓▓▓▓░  ▓▓▓█ ▒▓  ▓▓▓▓      
                                              ░▓▓▒                                                  
                                                                                                   
                                                                                                    
A JPK TIFF Image Processing and Metadata Extraction Toolkit

This repository contains a set of Python and FIJI (ImageJ) scripts to automate the preprocessing and metadata handling of scientific image data, particularly focused on JPK files and multi-channel TIFF stacks.

---

## 🔧 Setup Instructions

### 1. Python Environment

**Recommended:** Python 3.9+ with the following packages:

```bash
pip install numpy pandas matplotlib pillow tifffile openpyxl
```

Optional for extended TIFF support:

```bash
pip install imagecodecs
```

### 2. FIJI (ImageJ)

1. Download and install [FIJI (Fiji Is Just ImageJ)](https://fiji.sc/).
2. To use Python (Jython) scripts:

   * Launch FIJI.
   * Go to `Plugins > Scripting > Script Editor`.
   * Choose `Language > Python`.
   * Paste your `.py` script or load it from the script editor.
3. For macro usage: `.ijm` or `.py` scripts can also be run via `Plugins > Macros > Run` or from `Plugins > Scripting > Run Script`.

To integrate Python external scripts:

* Use `subprocess` in Jython scripts or execute Python scripts prior to/after FIJI workflows.

---

## 🗂️ File Overview

| Filename                               | Purpose                                                               |
| -------------------------------------- | --------------------------------------------------------------------- |
| `01_Excel_Parameters.py`               | Reads processing parameters from Excel.                               |
| `02_Extract_Channels.py`               | Extracts trace/retrace channels into separate TIFFs.                  |
| `02_Extract_Channels_Full_Metadata.py` | Same as above but also saves full metadata as `.txt`.                 |
| `02_Print_TIFF_Metadata.py`            | Prints all TIFF metadata to console for debugging.                    |
| `03_Merge_FIJI.py`                     | FIJI script: Merges two stacks and allows side-by-side visualization. |
| `04_Legend.py`                         | Adds metadata legend as overlay to the image stack.                   |
| `04_Legend copy.py`                    | Variant of the legend script, likely for experimentation.             |
| `04_User_Set_Scale.py`                 | Sets pixel scale from TIFF metadata with user interaction.            |
| `05_Final_Manual.py`                   | Manual version of the full FIJI image processing pipeline.            |
| `05_Final_Automatic.py`                | Fully automated FIJI image processing pipeline.                       |


## 🧩 Script Descriptions

### `01_Excel_Parameters.py`

Parses parameters from an Excel sheet (e.g., pixel size, channel labels) for batch processing scripts.

### `02_Extract_Channels.py`

Splits each JPK file into 18 TIFFs (9 channels × trace/retrace) based on binary format. Ideal for visualization in FIJI.

### `02_Extract_Channels_Full_Metadata.py`

Same as above, but saves complete metadata into `.txt` files alongside the TIFFs.

### `02_Print_TIFF_Metadata.py`

Reads and displays internal TIFF metadata (e.g., tags like pixel size) in human-readable format.

### `03_Merge_FIJI.py`

Lets users:

* Choose two image stacks (existing or from folder)
* View them side by side in FIJI
* Optionally save merged result with preserved metadata

### `04_Legend.py`

Draws metadata (e.g., pixel size, file name, parameters) as an overlay text at the end of the stack. Useful for publication.

### `04_User_Set_Scale.py`

Reads pixel dimensions and size from TIFF metadata and applies scale in FIJI. User is shown values and confirms application.

### `05_Final_Manual.py`

Step-wise manual processing pipeline for FIJI:

* Gaussian blur
* Drift correction
* Z-projection
* Plane leveling
* Metadata overlay

### `05_Final_Automatic.py`

Same as above but completely automated. User selects the stack or folder, and it runs without further prompts.

---

## ✅ Recommended Usage Order

1. Extract TIFFs and metadata:

   * `02_Extract_Channels_Full_Metadata.py`
2. Preview and debug TIFF metadata:

   * `02_Print_TIFF_Metadata.py`
3. Set correct scale in FIJI:

   * `04_User_Set_Scale.py`
4. Run the full pipeline:

   * Manual: `05_Final_Manual.py`
   * Automatic: `05_Final_Automatic.py`
5. Add legend for publication:

   * `04_Legend.py`

---

## 🧠 Notes

* You may adapt parameters per use case by modifying the scripts directly or using the Excel parameter reader.

---

## 📬 Contact

For issues, improvements, or questions, feel free to reach out to laura.mourelosoler@gmail.com
