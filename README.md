**BlendTextGuard** is a Blender add-on that safely imports **only** text blocks from one or more external `.blend` files into your current file—without executing any embedded scripts—and then generates a “flag report” listing any suspicious keywords detected.

---

## Features

- **Safe, Text-Only Import**  
  - Appends only the `Text` datablocks from every `.blend` in a chosen folder.  
  - Does **not** import any objects, materials, handlers, or executable logic from source files.

- **Case-Insensitive Keyword Scanning**  
  - By default scans for the following “suspicious” terms:  
    ```
    subprocess, os.system, urllib, requests, eval, exec, input, __import__, open, compile, bpy.app.handlers
    ```  
  - Lists all matches in a consolidated report.

- **Automatic Text Naming**  
  - Each imported text block is renamed to `<blend_filename>_<original_text_name>`.

- **Inline Error Handling**  
  - If a `.blend` file is corrupt or cannot be read, it is “skipped” (with a warning).  
  - All skipped filenames and their error messages appear in the final report.

- **On-Demand, In-Blender Report**  
  - Generates a new text datablock named `BlendTextGuard_FlagReport` if any suspicious keywords are found or any `.blend` files were skipped.  
  - Pops up a brief notification alerting you to open the report.

---

## Installation

1. **Download the BlendTextGuard as a ZIP**  
   - Click “Code → Download ZIP” on the GitHub repository for the BlendTextGuard folder.

2. **Install in Blender**  
   1. Open Blender and go to **Edit → Preferences → Add-ons → Install…**  
   2. Select the downloaded `BlendTextGuard.zip` (or the single `blend_text_guard.py` file).  
   3. Enable **BlendTextGuard** in the Add-ons list.

> **Note:** Requires **Blender 3.0** or newer.

---

## Getting Started

1. **Open a Text Editor area**  
   - In Blender’s workspace, switch one of the panels to **Text Editor**.

2. **Click “BlendTextGuard Append Folder”**  
   - In the Text Editor header menu, go to **Text → BlendTextGuard Append Folder**.

3. **Navigate to the folder you want to scan/append**  
   - In the file browser that appears, select the folder containing your `.blend` files.  
   - Click **Accept** (ensure the folder itself is selected, not a single file).

4. **View the report**  
   - When scanning/appending finishes, **BlendTextGuard_FlagReport** will open automatically.  
   - If any suspicious keywords were detected or any `.blend` files were skipped, you’ll see details in that report.

5. **Adjust the keyword list (optional)**  
   - Go to **Edit → Preferences → Add-ons**, search for **BlendTextGuard**, and expand its panel.  
   - Under “Suspicious Keywords,” edit the comma-separated list as needed.  
   - Click **Restore Default Keywords** to revert to the original set.

6. **Verify matches if found**  
   - If any suspicious keywords appear in the report, ensure you trust the publisher before running or using the imported scripts.
