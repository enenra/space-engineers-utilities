import bpy
import sys
import json
import addon_utils
import time

from bpy.types      import Operator
from bpy.props      import StringProperty

from .seut_utils    import get_preferences, wrap_text


def draw_bau_ui(self, context, element=None):

    wm = context.window_manager
    preferences = get_preferences()

    if element is None:
        layout = self.layout
    else:
        layout = element
    
    if addon_utils.check('blender_addon_updater') == (True, True):
        box = layout.box()
        row = box.row()
        row.label(text="Blender Addon Updater", icon='FILE_REFRESH')
    
        if __package__ in wm.bau.addons:
            addon = sys.modules.get(__package__)
            current_version_name = str(addon.bl_info['version']).replace("(","").replace(")","").replace(", ", ".")
            bau_entry = wm.bau.addons[__package__]

            col = row.column(align=True)
            row = col.row()
            row.alignment = 'RIGHT'

            row = row.row(align=True)
            op = row.operator('wm.bau_save_config', text="", icon='FILE_TICK')
            op.name = __package__
            op.config = str(get_config())
            op = row.operator('wm.url_open', text="Releases", icon='URL')
            op.url = addon.bl_info['git_url'] + "/releases"
            op = row.operator('wm.bau_unregister_addon', text="", icon='UNLINKED')
            op.name = __package__
            
            row = box.row(align=True)
            row.scale_y = 2.0
            split = row.split(align=True)

            if not bau_entry.dev_mode and bau_entry.rel_ver_needs_update:
                split.alert = True
                op = split.operator('wm.bau_update_addon', text="Update available: " + bau_entry.latest_rel_ver_name, icon='IMPORT')
                op.name = __package__
                op.config = str(get_config())
                op.display_instructions = True

            elif bau_entry.dev_mode and bau_entry.dev_ver_needs_update:
                split.alert = True
                op = split.operator('wm.bau_update_addon', text="Update available: " + bau_entry.latest_dev_ver_name, icon='IMPORT')
                op.name = __package__
                op.config = str(get_config())
                op.display_instructions = True

            else:
                if not preferences.dev_mode:
                    split.operator('wm.bau_update_addon', text="Up to date: " + current_version_name, icon='CHECKMARK')
                else:
                    split.operator('wm.bau_update_addon', text="Up to date: " + current_version_name + "-" + addon.bl_info['dev_tag'] + "." + str(addon.bl_info['dev_version']), icon='CHECKMARK')
                split.enabled = False

            if bau_entry.display_instructions:
                split.enabled = False

            split = row.split(align=True)
            op = split.operator('wm.bau_check_updates', text="", icon='FILE_REFRESH')
            op.name = __package__
            
            split = row.split(align=True)
            split.prop(bau_entry, 'dev_mode', text="", icon='SETTINGS')

            row = box.row(align=True)
            row.alignment = 'RIGHT'
            if bau_entry.connection_status != "Connected.":
                row.alert = True
                row.label(text=bau_entry.connection_status, icon='CANCEL')
            else:
                row.label(text= "Last check: " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(bau_entry.last_check)))

            if bau_entry.display_instructions:
                show_instructions(context, box)
            else:
                if not bau_entry.dev_mode and bau_entry.rel_ver_needs_update:
                    show_changelog(addon, box, bau_entry.rel_changelog, bau_entry.latest_rel_ver_name)

                elif bau_entry.dev_mode and bau_entry.dev_ver_needs_update:
                    show_changelog(addon, box, bau_entry.dev_changelog, bau_entry.latest_dev_ver_name)
        
        else:
            col = row.column(align=True)
            op = col.operator('wm.bau_register_addon', text="", icon='LINK_BLEND')
            op.name = __package__
            op.display_changelog = True
            op.download_method = 'asset'
            op.dev_mode = preferences.dev_mode


def show_instructions(context, box):
    box = box.box()

    row = box.row()
    row.alert = True
    row.label(text="Installation Instructions", icon='ERROR')

    lines = wrap_text(f"Only perform this update in a fresh, empty BLEND file! Otherwise, there is a chance that data may be lost or corrupted. You may have to restart Blender in order for the addon to be enabled and working.", int(context.region.width / 7))
    for l in lines:
        row = box.row()
        row.scale_y = 0.5
        row.alert = True
        row.label(text=l)
    
    box.separator()

    row = box.row(align=True)
    row.scale_y = 2.0
    op = row.operator('wm.bau_update_addon', text="Everything is ready - Update!", icon='IMPORT')
    op.name = __package__
    op.config = str(get_config())
    op.display_instructions = False


def show_changelog(addon, box, changelog, latest_ver_name):

    if changelog != "":
        text = json.loads(changelog)

        box = box.box()
        row = box.row(align=True)
        row.label(text="Changelog", icon='FILE_TEXT')

        counter = 0
        for item in text:
            if counter > 10:
                split = box.split(factor=0.75)
                split.label(text="...")

                op = split.operator('wm.url_open', text="Read More")
                op.url = addon.bl_info['git_url'] + "/releases/" + "v" + latest_ver_name
                break

            row = box.row()
            row.scale_y = 0.5
            row.label(text=item)
            counter += 1


def get_config() -> dict:
    """Saves params from preferences to dict for json."""

    preferences = get_preferences()
    data = {}
    data['space-engineers-utilities'] = []
    dict = {}

    if preferences.game_path is not None:
        dict['game_path'] = preferences.game_path
    if preferences.game_path is not None:
        dict['asset_path'] = preferences.asset_path
    if preferences.game_path is not None:
        dict['mwmb_path'] = preferences.mwmb_path
    if preferences.game_path is not None:
        dict['havok_path'] = preferences.havok_path

    data['space-engineers-utilities'].append(dict)
    return data


def set_config(data):
    """Gets params from dict and saves it to preferences."""

    preferences = get_preferences()

    if 'space-engineers-utilities' in data:
        cfg = data['space-engineers-utilities'][0]
        if 'game_path' in cfg:
            preferences.game_path = cfg['game_path']
        if 'asset_path' in cfg:
            preferences.asset_path = cfg['asset_path']
        if 'mwmb_path' in cfg:
            preferences.mwmb_path = cfg['mwmb_path']
        if 'havok_path' in cfg:
            preferences.havok_path = cfg['havok_path']


def bau_register():
    wm = bpy.context.window_manager

    try:
        if __package__ not in wm.bau.addons:
            result = bpy.ops.wm.bau_register_addon(name=__package__, display_changelog=True, download_method='asset', dev_mode=get_preferences().dev_mode)
            if not result == {'FINISHED'}:
                return 5.0
        bpy.app.timers.unregister(bau_register)
    except:
        return 5.0