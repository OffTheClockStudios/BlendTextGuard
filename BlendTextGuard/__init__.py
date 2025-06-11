bl_info = {
    "name": "BlendTextGuard",
    "author": "OffTheClock Studios",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "Text Editor > Text > BlendTextGuard Append Folder",
    "description": "Safely appends only text blocks from external .blend files into the current file without running any embedded scripts",
    "warning": "",
    "category": "Text Editor",
}

import bpy
import os
import traceback

from bpy.types import Operator
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper


# -------------------------------------------------------------------
# 1) PREFERENCES SECTION
# -------------------------------------------------------------------
class BlendTextGuardPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    flag_keywords: StringProperty(
        name="Suspicious Keywords",
        default=(
            "subprocess,os.system,urllib,requests,eval,exec,input,__import__,open,compile,bpy.app.handlers,"
            "socket,http.client,ftplib,base64,64,hex,unicode_escape,bytes.fromhex,codecs,marshal,zlib,bz2,"
            "gzip,rot13,re,inspect,ctypes,getattr,setattr,globals,locals,__dict__"
        ),
        description="Comma-separated keywords to scan for (case-insensitive)"
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "flag_keywords")
        layout.operator("blendtextguard.reset_preferences", icon='RECOVER_LAST')



class BLENDTEXTGUARD_OT_ResetPrefs(bpy.types.Operator):
    bl_idname = "blendtextguard.reset_preferences"
    bl_label = "Restore Default Keywords"
    bl_description = "Reset the keyword list to its default values"

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        prefs.flag_keywords = (
            "subprocess,os.system,urllib,requests,eval,exec,input,__import__,open,compile,bpy.app.handlers,"
            "socket,http.client,ftplib,base64,64,hex,unicode_escape,bytes.fromhex,codecs,marshal,zlib,bz2,"
            "gzip,rot13,re,inspect,ctypes,getattr,setattr,globals,locals,__dict__"
        )
        self.report({'INFO'}, "BlendTextGuard keywords reset to defaults.")
        return {'FINISHED'}


# -------------------------------------------------------------------
# 2) SCANNING + APPENDING HELPERS (updated)
# -------------------------------------------------------------------
def scan_text_for_flags(text_block, flag_keywords):
    """
    Returns a list of keywords (from flag_keywords) found in text_block.
    Matching is done case-insensitively, but we leave the text itself unchanged.
    """
    content = text_block.as_string()
    content_lower = content.lower()
    matched = []
    for kw in flag_keywords:
        if kw.lower() in content_lower:
            matched.append(kw)
    return matched


def append_texts_from_blend(blend_path, existing_names, flag_keywords, flagged_results):
    """
    Given a .blend path, append all its text blocks into the current file.
    Rename each new text block by prefixing with the blend filename.
    Scan each newly added text for any keywords (case-insensitive) and record matches.
    Returns (number_of_new_blocks, first_new_text_reference).
    """
    blend_name = os.path.splitext(os.path.basename(blend_path))[0]
    new_count = 0
    first_new = None

    # 1) Capture names before loading
    before_names = {t.name for t in bpy.data.texts}

    # 2) Load only the "Text" datablocks from that .blend
    with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
        if not data_from.texts:
            return (0, None)  # no text blocks to import
        data_to.texts = data_from.texts

    # 3) After loading, figure out which text names were newly added
    after_names = {t.name for t in bpy.data.texts}
    new_names = after_names - before_names

    for original_name in new_names:
        # Skip if somehow name was already in existing_names (collision)
        if original_name in existing_names:
            continue

        # Get the text datablock object
        txt = bpy.data.texts.get(original_name)
        if not txt:
            continue

        # Construct a new name
        new_name = f"{blend_name}_{original_name}"
        # If that new_name already exists from a previous run, remove it
        if new_name in bpy.data.texts:
            bpy.data.texts.remove(bpy.data.texts[new_name])

        # Rename the block exactly once
        txt.name = new_name
        new_count += 1

        # Scan for any suspicious keywords
        matched = scan_text_for_flags(txt, flag_keywords)
        if matched:
            # Store (blend_name, original_name, matches)
            flagged_results.append((blend_name, original_name, matched))

        # Track the very first imported text for showing in the Text Editor
        if first_new is None:
            first_new = txt

    return (new_count, first_new)


# -------------------------------------------------------------------
# 3) REPORT GENERATION HELPER (updated)
# -------------------------------------------------------------------
def generate_and_show_flag_report(flagged_results, flag_keywords, skipped_files):
    """
    Create (or overwrite) a Text block named "BlendTextGuard_FlagReport".
    Write a formatted report of:
      - Any skipped .blend files (with the load-error messages).
      - All flagged text blocks, showing (blend_name, original_name, matched keywords).
      - A promotional footer.
    Show it in the Text Editor.
    """
    report_name = "BlendTextGuard_FlagReport"

    # Remove old report if it exists
    if report_name in bpy.data.texts:
        bpy.data.texts.remove(bpy.data.texts[report_name])

    report = bpy.data.texts.new(report_name)

    # Header
    report.write("BlendTextGuard Security Scan Report\n")
    report.write("=" * 35 + "\n\n")

    # 1) List skipped files (if any)
    if skipped_files:
        report.write("Skipped .blend files (could not load):\n")
        for fname, err in skipped_files:
            report.write(f"  • {fname}  ⇒  {err}\n")
        report.write("\n" + "-" * 35 + "\n\n")

    # 2) List flagged text blocks
    report.write(f"Keywords scanned (case-insensitive match): {', '.join(flag_keywords)}\n\n")
    if flagged_results:
        for blend_name, original_name, matches in flagged_results:
            report.write(f">> Blend File: {blend_name}\n")
            report.write(f"   Block: {original_name}\n")
            report.write(f"   Matched: {', '.join(matches)}\n\n")
    else:
        report.write("No flagged text blocks found.\n\n")

    # 3) Promotional line at the end
    report.write("-" * 35 + "\n")
    report.write("Check out other add-ons from OffTheClockStudios:\n")
    report.write("https://superhivemarket.com/creators/offtheclockstudiosstore\n")

    # Open the report in the Text Editor, then jump cursor to line 1
    for area in bpy.context.window.screen.areas:
        if area.type == 'TEXT_EDITOR':
            space = area.spaces.active
            space.text = report

            for region in area.regions:
                if region.type == 'WINDOW':
                    bpy.ops.text.jump(line=1)
                    break
            break

    # Show a popup if there are flagged results or skipped files
    def draw_popup(self, context):
        lines = []
        if skipped_files:
            lines.append("⚠ Skipped one or more .blend files.")
        if flagged_results:
            lines.append("⚠ Flagged text blocks detected.")
        for l in lines:
            self.layout.label(text=l)
        if lines:
            self.layout.label(text="See 'BlendTextGuard_FlagReport' for details.")

    if skipped_files or flagged_results:
        bpy.context.window_manager.popup_menu(
            draw_popup,
            title="BlendTextGuard Scan Report",
            icon='ERROR'
        )


# -------------------------------------------------------------------
# 4) MAIN OPERATOR (tracks skipped_files, unchanged)
# -------------------------------------------------------------------
class BlendTextGuardOpenTextsFromBlendsInFolder(Operator, ImportHelper):
    bl_idname = "text.blend_text_guard_open_texts_from_blend_folder"
    bl_label = "BlendTextGuard Append Folder"
    bl_description = "Safely import only text blocks from .blend files in a selected folder"
    directory: StringProperty(subtype='DIR_PATH')

    def execute(self, context):
        blend_files = [f for f in os.listdir(self.directory) if f.lower().endswith(".blend")]
        if not blend_files:
            self.report({'WARNING'}, "No .blend files found in the selected folder.")
            return {'CANCELLED'}

        prefs = context.preferences.addons[__name__].preferences
        flag_keywords = [kw.strip() for kw in prefs.flag_keywords.split(",") if kw.strip()]

        flagged_results = []
        skipped_files = []
        total_count = 0
        processed_files = 0
        first_new_text = None

        for fname in blend_files:
            blend_path = os.path.join(self.directory, fname)
            existing_names = {t.name for t in bpy.data.texts}

            try:
                new_count, first_txt = append_texts_from_blend(
                    blend_path, existing_names, flag_keywords, flagged_results
                )
            except Exception as e:
                skipped_files.append((fname, str(e)))
                print(f"[BlendTextGuard] Error loading '{blend_path}':")
                traceback.print_exc()
                continue

            total_count += new_count
            processed_files += 1
            if first_new_text is None and first_txt:
                first_new_text = first_txt

        # Show the very first appended text block if available
        if first_new_text and context.area.type == 'TEXT_EDITOR':
            context.space_data.text = first_new_text

        # Generate report if needed
        if skipped_files or flagged_results:
            generate_and_show_flag_report(flagged_results, flag_keywords, skipped_files)

        # Final summary in the Info area
        if total_count == 0 and not skipped_files:
            self.report({'INFO'}, f"No text blocks found in {len(blend_files)} file(s).")
        else:
            file_label = "file" if processed_files == 1 else "files"
            summary_parts = []
            if total_count:
                summary_parts.append(f"Appended {total_count} text block(s) from {processed_files} {file_label}.")
            if skipped_files:
                summary_parts.append(f"Skipped {len(skipped_files)} .blend file(s).")
            self.report({'INFO'}, "  ".join(summary_parts))

        return {'FINISHED'}


# -------------------------------------------------------------------
# 5) UI DRAWER AND REGISTRATION (unchanged)
# -------------------------------------------------------------------
def draw_blend_text_guard_append_option(self, context):
    self.layout.separator()
    self.layout.operator(BlendTextGuardOpenTextsFromBlendsInFolder.bl_idname, icon='IMPORT')


def register():
    bpy.utils.register_class(BlendTextGuardPreferences)
    bpy.utils.register_class(BLENDTEXTGUARD_OT_ResetPrefs)
    bpy.utils.register_class(BlendTextGuardOpenTextsFromBlendsInFolder)
    bpy.types.TEXT_MT_text.append(draw_blend_text_guard_append_option)


def unregister():
    bpy.types.TEXT_MT_text.remove(draw_blend_text_guard_append_option)
    bpy.utils.unregister_class(BlendTextGuardOpenTextsFromBlendsInFolder)
    bpy.utils.unregister_class(BLENDTEXTGUARD_OT_ResetPrefs)
    bpy.utils.unregister_class(BlendTextGuardPreferences)


if __name__ == "__main__":
    register()
