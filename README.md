
# 🛡️ BlendTextGuard – Secure Text Import from `.blend` Files
---
---

**BlendTextGuard** is a Blender add-on that safely imports **only** text blocks from one or more external `.blend` files into your current file—**without executing any embedded scripts**—and then generates a “flag report” listing any suspicious keywords detected.

While it's possible to open `.blend` files without auto-running Python, this tool lets you **batch-scan multiple `.blend` files at once**. The benefit is bringing all scripts into a **controlled environment** and scanning them **in bulk** for suspicious terms.

---
---

## ✨ Features

### ✅ Safe, Text-Only Import  
- Appends only the `Text` datablocks from each `.blend` in a selected folder.  
- Does **not** import any objects, materials, handlers, or executable logic.

### 🔍 Case-Insensitive Keyword Scanning  
- Scans for potentially dangerous terms like:
  ```
  subprocess, os.system, urllib, requests, eval, exec, input, __import__, open, compile, bpy.app.handlers
  ```
- Matches are shown in a consolidated, readable report.

### 🧾 Automatic Text Naming  
- Imported text blocks are renamed to:  
  ```
  <blend_filename>_<original_text_name>
  ```

### ⚠️ Inline Error Handling  
- If a `.blend` file is corrupt or unreadable, it’s **skipped gracefully**.  
- Skipped files and error messages appear in the final report.

### 📝 In-Blender Flag Report  
- If any suspicious keywords are found (or files skipped), a new text block is created:
  ```
  BlendTextGuard_FlagReport
  ```
- A popup alerts you to view the report after the scan.

---
---

## 🔧 Installation (from GitHub)

**Download BlendTextGuard as a ZIP**  
 - Visit the GitHub repository and click "Download ZIP" or "Download Raw File". 
 - Open **Blender → Edit → Preferences → Add-ons → Install…**  
 - Select the `BlendTextGuard.zip` file.  
 - Enable the **BlendTextGuard** add-on in the list.

> 💡 **Requires Blender 3.0 or newer.**

---

## 🔧 Installation (from Blender – Pending Inclusion)

**Download BlendTextGuard as an Extension**  
 - Open **Blender → Edit → Preferences → Get Extensions...**  
 - Search for **BlendTextGuard**  
 - Click **Install**

> 💡 **Requires Blender 3.0 or newer.**

---
---

## 🚀 Getting Started

1. **Open a Text Editor area**: Change one of Blender's panels to the **Text Editor**.

2. **Launch the tool**: Go to **Text → BlendTextGuard Append Folder**.

3. **Select the folder to scan**: Choose a folder containing one or more `.blend` files. Click **Accept** (select the folder, not a file).

4. **View the generated report**: After import, the report appears in the Text Editor if anything was flagged. It includes skipped files and any suspicious keyword matches.

5. **Customize suspicious keywords (optional)**: Go to **Edit → Preferences → Add-ons → BlendTextGuard**. Modify the comma-separated keyword list as needed. Use **"Restore Default Keywords"** to reset.

6. **Manually review any flagged results**: Even if a script is flagged, **it is not run automatically**. Always review text content before clicking **Run Script**.

---
---

# Suspicious Keywords (Breakdown)
 ### 🛠️ System/Execution
`subprocess, os.system, urllib, requests, eval, exec, input, __import__, open, compile, bpy.app.handlers`

📝 _Explanation:_ These functions or modules directly execute or dynamically evaluate code. They’re commonly used in exploits.

### 🌐 Network/Remote Access
`urllib, requests, socket, http.client, ftplib`

📝 _Explanation:_ Modules that allow external network communication, which can be used for data exfiltration or remote control.

### 🧪 Obfuscation, Encoding, and Conversion
`base64, 64, hex, unicode_escape, bytes.fromhex, codecs, marshal, zlib, bz2, gzip, rot13, re`
    
📝 _Explanation:_ These are frequently used to disguise malicious payloads or scripts (e.g., encoded payloads decoded at runtime and used in complex obfuscation via regex).

### 🔧 Misc/Advanced
`inspect, ctypes, getattr, setattr, globals, locals, dict`

📝 _Explanation:_ These identifiers enable deep runtime manipulation or dynamic code behavior and are commonly used in more sophisticated or stealthy attacks.

## ⚠️ Disclaimer

**BlendTextGuard is a scanning tool—not a sandbox or script blocker.**

- It helps reduce risk but **does not guarantee 100% safety**:
  - Scans for suspicious keywords only (which are customizable).
  - It does not prevent users from running scripts manually.
  - Malicious logic might still be obfuscated or cleverly bypass detection.

- Use it as part of a broader pipeline:
  - Manually inspect any imported code.
  - Use version control and backups.
  - Consider signing scripts or using sandboxed workflows in critical projects.

---
---

