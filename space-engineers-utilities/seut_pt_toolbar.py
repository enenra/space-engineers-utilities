import bpy
import addon_utils

from bpy.types  import Panel

from .utils.seut_patch_blend        import check_patch_needed
from .seut_collections              import get_collections, seut_collections
from .seut_utils                    import get_enum_items, wrap_text, get_seut_blend_data


def check_display_panels(context) -> bool:
    scene = context.scene
    return not check_patch_needed() and 'SEUT' in scene.view_layers

class SEUT_PT_Panel(Panel):
    """Creates the topmost panel for SEUT"""
    bl_idname = "SEUT_PT_Panel"
    bl_label = "Space Engineers Utilities"
    bl_category = "SEUT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        wm = context.window_manager
        data = get_seut_blend_data()

        if bpy.app.version < (3, 0, 0):
            row = layout.row()
            row.alert = True
            row.scale_y = 0.75
            row.label(text="SEUT requires Blender 3.0+.")
            row = layout.row()
            row.alert = True
            row.scale_y = 0.75
            row.label(text="Please update your Blender installation!")
            return
        
        skip = False
        repo = None
        try:
            for r in data.seut.repos:
                if r.needs_update:
                    if r.current_version == '0.0.0':
                        continue
                    else:
                        repo = r
        except KeyError:
            skip = True
        
        if addon_utils.check('blender_addon_updater') == (True, True) and __package__ in wm.bau.addons:
            bau_entry = wm.bau.addons[__package__]
            if not bau_entry.dev_mode and bau_entry.rel_ver_needs_update or bau_entry.dev_mode and bau_entry.rel_ver_needs_update:
                row = layout.row()
                row.alert = True
                row.label(text="SEUT Update Available", icon='ERROR')
                row = layout.row()
                row.label(text="Go to Addon Preferences to update.")
            elif not skip and repo is not None and repo.needs_update:
                if tuple(map(int, repo.current_version.split('.'))) > tuple(map(int, repo.latest_version.split('.'))) and repo.dev_mode:
                    pass
                else:
                    row = layout.row()
                    row.alert = True
                    row.label(text=f"Update for {repo.text_name} available.", icon='ERROR')
                    row = layout.row()
                    row.label(text="Go to Addon Preferences to update.")

        else:
            if not skip and repo is not None and repo.needs_update:
                if tuple(map(int, repo.current_version.split('.'))) > tuple(map(int, repo.latest_version.split('-')[0].split('.'))) and repo.dev_mode:
                    pass
                else:
                    row = layout.row()
                    row.alert = True
                    row.label(text=f"Update for {repo.text_name} available.", icon='ERROR')
                    row = layout.row()
                    row.label(text="Go to Addon Preferences to update.")

        if not 'SEUT' in scene.view_layers:
            row = layout.row()
            row.scale_y = 2.0
            row.operator('scene.recreate_collections', text="Initialize SEUT Scene", icon='OUTLINER')

            if 'RenderLayer' in scene.view_layers:
                row = layout.row()
                row = layout.row()
                row.scale_y = 2.0
                row.operator('wm.convert_structure', icon='OUTLINER')

        else:
            if check_patch_needed():
                row = layout.row()
                row.scale_y = 2.0
                row.operator('wm.patch_blend', icon='OUTLINER')
                
            else:

                # SubtypeId
                box = layout.box()
                split = box.split(factor=0.85)
                split.label(text=scene.name, icon_value=layout.icon(scene))
                link = split.operator('wm.semref_link', text="", icon='INFO')
                link.section = 'reference'
                link.page = '6094866/SEUT+Main+Panel'

                box.prop(scene.seut, 'sceneType')
                if scene.seut.sceneType == 'mainScene' or scene.seut.sceneType == 'subpart':
                    if scene.seut.linkSubpartInstances:
                        col = box.column(align=True)
                        row = col.row(align=True)
                        row.operator('scene.update_subpart_instances', icon='MOD_INSTANCE')
                        row.prop(scene.seut,'linkSubpartInstances', text='', icon='UNLINKED', invert_checkbox=True)
                    else:
                        box.prop(scene.seut,'linkSubpartInstances', icon='LINKED')

                row = box.row(align=True)
                row.prop(context.view_layer, '["paint_color"]', text='Paint Color')
                
                box = layout.box()
                if scene.seut.sceneType == 'mainScene':
                    box.label(text="SubtypeId (File Name)", icon='COPY_ID')
                else:
                    box.label(text="File Name", icon='FILE')
                box.prop(scene.seut, "subtypeId", text="", expand=True)

                if scene.seut.sceneType == 'mainScene' or scene.seut.sceneType == 'subpart':
                    box = layout.box()
                    box.label(text="Grid Scale", icon='GRID')
                    row = box.row()
                    row.prop(scene.seut,'gridScale', expand=True)
                            
                split = layout.split(factor=0.85)
                col = split.column()

                row = col.row()
                if data.seut.issue_alert:
                    row.alert = True
                row.operator('wm.issue_display', icon='INFO')
                
                col = split.column()
                col.prop(data.seut, 'simple_navigation', text="", icon='OUTLINER')


class SEUT_PT_Panel_Collections(Panel):
    """Creates the collections panel for SEUT"""
    bl_idname = "SEUT_PT_Panel_Collections"
    bl_label = "Collections"
    bl_category = "SEUT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return (scene.seut.sceneType == 'mainScene' or scene.seut.sceneType == 'subpart' or scene.seut.sceneType == 'character') and check_display_panels(context)


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        active_col = context.view_layer.active_layer_collection.collection

        show_button = True
        if active_col.seut.col_type != 'none':
            box = layout.box()
            box.label(text=active_col.name, icon='COLLECTION_' + active_col.color_tag)
            if active_col.seut.col_type in seut_collections[scene.seut.sceneType]:
                row = box.row(align=True)
                row.label(text=seut_collections[scene.seut.sceneType][active_col.seut.col_type]['type'])
                if active_col.seut.col_type == 'hkt':
                    link = row.operator('wm.semref_link', text="", icon='INFO')
                    link.section = 'tutorials'
                    link.page = '10944513/Create+Collision+Model+Tutorial'
            elif active_col.seut.col_type == 'seut':
                box.label(text='SEUT Collection Container')

            if not active_col.seut.col_type == 'seut':
                if not active_col.seut.col_type in seut_collections[scene.seut.sceneType] or active_col.seut.ref_col is not None and not active_col.seut.ref_col.seut.col_type in seut_collections[scene.seut.sceneType]:
                    show_button = False
                    lines = wrap_text(f"Collection type not supported by scene type '{get_enum_items(scene.seut, 'sceneType', scene.seut.sceneType)[0]}'.", int(context.region.width / 8.5))
                    for l in lines:
                        row = box.row()
                        row.scale_y = 0.75
                        row.alert = True
                        row.label(text=l)

        if active_col.seut.col_type in ['lod', 'hkt']:
            split = box.split(factor=0.35)
            col = split.column()
            row = col.row()
            if active_col.seut.ref_col is None:
                row.alert = True
            row.label(text="Reference:")
            col = split.column()
            row = col.row()
            if active_col.seut.ref_col is None:
                row.alert = True
            row.prop(active_col.seut,'ref_col', text="")

            if active_col.seut.col_type == 'lod':
                box.prop(active_col.seut,'lod_distance')
            elif active_col.seut.col_type == 'hkt':
                box.prop(active_col.seut,'hkt_file')

        if show_button:
            row = layout.row()
            row.scale_y = 1.5
            row.operator('scene.create_collection')
            layout.operator('scene.recreate_collections', icon='OUTLINER')


class SEUT_PT_Panel_BoundingBox(Panel):
    """Creates the bounding box panel for SEUT"""
    bl_idname = "SEUT_PT_Panel_BoundingBox"
    bl_label = "Bounding Box"
    bl_category = "SEUT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'mainScene' and check_display_panels(context)


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        data = get_seut_blend_data()

        # Toggle
        layout.prop(data.seut,'bBox', expand=True)

        if data.seut.bBox == 'on':
            # Size
            box = layout.box()
            box.label(text="Size", icon='PIVOT_BOUNDBOX')
            row = box.row()
            row.prop(scene.seut, "bBox_X")
            row.prop(scene.seut, "bBox_Y")
            row.prop(scene.seut, "bBox_Z")

            row = box.row()
            row.prop(data.seut, 'bBox_color', text="")


class SEUT_PT_Panel_Mirroring(Panel):
    """Creates the mirroring panel for SEUT"""
    bl_idname = "SEUT_PT_Panel_Mirroring"
    bl_label = "Mirroring Mode"
    bl_category = "SEUT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'mainScene' and check_display_panels(context)


    def draw(self, context):
        layout = self.layout
        scene = context.scene

        if scene.seut.mirroringToggle == 'on':
            split = layout.split(factor=0.85)
            row = split.row()
            row.prop(scene.seut, 'mirroringToggle', expand=True)
            link = split.operator('wm.semref_link', text="", icon='INFO')
            link.section = 'tutorials'
            link.page = '6095170/Mirroring+Tutorial'
            
            layout.prop(scene.seut, 'mirroringScene', text="Model", icon='MOD_MIRROR')
        else:
            layout.prop(scene.seut, 'mirroringToggle', expand=True)


class SEUT_PT_Panel_Mountpoints(Panel):
    """Creates the mountpoints panel for SEUT"""
    bl_idname = "SEUT_PT_Panel_Mountpoints"
    bl_label = "Mountpoint Mode"
    bl_category = "SEUT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'mainScene' and check_display_panels(context)


    def draw(self, context):
        layout = self.layout
        scene = context.scene

        if scene.seut.mountpointToggle == 'on':
            split = layout.split(factor=0.85)
            row = split.row()
            row.prop(scene.seut, 'mountpointToggle', expand=True)
            link = split.operator('wm.semref_link', text="", icon='INFO')
            link.section = 'tutorials'
            link.page = '6160894/Mountpoint+Tutorial'

            if not context.active_object is None and context.active_object.name in bpy.data.collections['Mountpoints (' + scene.seut.subtypeId + ')'].objects and not context.active_object.type == 'EMPTY':
                box = layout.box()
                box.label(text="Area", icon='MESH_PLANE')
                box.prop(context.active_object.seut, 'enabled', icon='CHECKBOX_HLT')
                if context.active_object.seut.enabled:
                    row = box.row()
                    row.prop(context.active_object.seut, 'default', icon='PINNED')
                    row.prop(context.active_object.seut, 'pressurized', icon='LOCKED', text="Pressurized")

                    box.prop(context.active_object.seut, 'mask_preset', text="Mask")
                    if context.active_object.seut.mask_preset == 'custom':
                        box.prop(context.active_object.seut, 'exclusion_mask')
                        box.prop(context.active_object.seut, 'properties_mask')
                
            layout.operator('scene.add_mountpoint_area', icon='ADD')
        else:
            layout.prop(scene.seut, 'mountpointToggle', expand=True)
        

class SEUT_PT_Panel_IconRender(Panel):
    """Creates the mirroring panel for SEUT"""
    bl_idname = "SEUT_PT_Panel_IconRender"
    bl_label = "Icon Render Mode"
    bl_category = "SEUT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'mainScene' and check_display_panels(context)


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        layout.prop(scene.seut, 'renderToggle', expand=True)

        camera = None
        for cam in bpy.data.cameras:
            if cam.name == 'ICON':
                camera = cam
        empty = None
        for obj in bpy.data.objects:
            if obj.type == 'EMPTY' and obj.name == 'Icon Render':
                empty = obj

        if scene.seut.renderToggle == 'on':
            layout.operator('scene.icon_render_preview', icon='RENDER_RESULT')

            box = layout.box()
            box.label(text='View', icon='CAMERA_DATA')
            if camera is not None:
                box.prop(scene.seut, 'renderZoom')
            
            keyLight = None
            fillLight = None
            rimLight = None
            for obj in bpy.data.objects:
                if obj.type == 'LIGHT':
                    if obj.name == 'Key Light':
                        keyLight = obj
                    elif obj.name == 'Fill Light':
                        fillLight = obj
                    elif obj.name == 'Rim Light':
                        rimLight = obj
                        
            if camera is not None and keyLight is not None and fillLight is not None and rimLight is not None:
                box.prop(scene.seut, 'renderDistance')

            if empty is not None:
                box.prop(scene.seut, 'renderEmptyLocation')
            if empty is not None:
                box.prop(scene.seut, 'renderEmptyRotation')

            box = layout.box()
            split = box.split(factor=0.85)
            col = split.column()
            col.label(text='Options', icon='SETTINGS')
            col = split.column()
            col.operator('scene.copy_render_options', text="", icon='PASTEDOWN')

            box.prop(scene.seut, 'renderColorOverlay', invert_checkbox=True)
            box.prop(scene.seut, 'renderResolution')
            box.prop(scene.seut, 'render_output_type')
            
            box.prop(scene.render, 'filepath', text="Folder", expand=True)


class SEUT_PT_Panel_Export(Panel):
    """Creates the export panel for SEUT"""
    bl_idname = "SEUT_PT_Panel_Export"
    bl_label = "Export"
    bl_category = "SEUT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType in ['mainScene', 'subpart', 'character', 'character_animation'] and check_display_panels(context)


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        data = get_seut_blend_data()

        # Export
        row = layout.row()
        row.scale_y = 2.0
        row.operator('scene.export_all_scenes', icon='EXPORT')
        row = layout.row()
        row.scale_y = 1.1
        row.operator('scene.export', icon='EXPORT')

        if scene.seut.sceneType in ['mainScene', 'subpart']:
            layout.operator('animation.export', icon='DECORATE_DRIVER')
        
        split = layout.split(factor=0.85, align=True)
        split.operator('scene.export_materials', icon='EXPORT')
        link = split.operator('wm.semref_link', text="", icon='INFO')
        link.section = 'tutorials'
        link.page = '6128098/Create+MatLib+Tutorial'

        # Options
        box = layout.box()
        split = box.split(factor=0.85)
        col = split.column()
        col.label(text="Options", icon='SETTINGS')
        col = split.column()
        col.operator('scene.copy_export_options', text="", icon='PASTEDOWN')
    
        box.prop(scene.seut, "export_deleteLooseFiles", icon='TEMP')
        box.prop(data.seut, "convert_textures", icon='NODE_TEXTURE')
        row = box.row()
        if scene.seut.sceneType not in ['character', 'character_animation']:
            row.prop(scene.seut, "export_sbc_type", expand=True)

        if scene.seut.sceneType != 'character' and scene.seut.sceneType != 'character_anmiation':
            box2 = box.box()
            box2.label(text="Grid Export", icon='GRID')
            split = box2.split(factor=0.5)
            col = split.column(align=True)
            col.prop(scene.seut, "export_largeGrid", icon='MESH_CUBE')
            col = split.column(align=True)
            col.prop(scene.seut, "export_smallGrid", icon='META_CUBE')
            if scene.seut.export_smallGrid:
                col.prop(scene.seut, "export_medium_grid", icon='CUBE')
        
        box.prop(scene.seut, "mod_path", text="Mod")
        if scene.seut.mod_path != "":
            box.prop(scene.seut, "export_exportPath", text="Model")


class SEUT_PT_Panel_Import(Panel):
    """Creates the import panel for SEUT"""
    bl_idname = "SEUT_PT_Panel_Import"
    bl_label = "Import"
    bl_category = "SEUT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType in ['mainScene', 'subpart', 'character', 'character_animation'] and check_display_panels(context)


    def draw(self, context):

        scene = context.scene
        data = get_seut_blend_data()
        layout = self.layout

        # Import

        row = layout.row()
        row.scale_y = 2.0
        row.operator('scene.import', icon='IMPORT')

        layout.operator('scene.import_complete', icon='IMPORT')
        
        box = layout.box()
        box.label(text='Options', icon='SETTINGS')

        if addon_utils.check("better_fbx") == (True, True):
            box.prop(data.seut, 'better_fbx', icon='CHECKMARK')

        box.prop(data.seut, 'fix_scratched_materials', icon='MATERIAL')

        # Repair
        box = layout.box()
        box.label(text="Repair", icon='TOOL_SETTINGS')
        row = box.row(align=True)
        row.operator('object.remapmaterials', icon='MATERIAL')
        row.prop(data.seut, 'remap_all', text="", icon='SCENE_DATA')
        box.operator('wm.convert_structure', icon='OUTLINER')

        box2 = box.box()
        row = box2.row()
        row.label(text="Model Fixes", icon='EMPTY_AXIS')
        row.alignment = 'RIGHT'
        link = row.operator('wm.semref_link', text="", icon='INFO')
        link.section = 'tutorials'
        link.page = '71827457'

        col = box2.column(align=True)
        col.operator('object.apply_scale_rotation', icon='ORIENTATION_GIMBAL')
        col.operator('object.fix_positioning', icon='TRACKING_CLEAR_FORWARDS')
        col.operator('object.apply_location', icon='CON_OBJECTSOLVER')

        if scene.seut.sceneType == 'character' or scene.seut.sceneType == 'character_animation':
            # Bones
            box = layout.box()
            box.label(text="Bone Conversion", icon='ARMATURE_DATA')
            box.operator('object.convertbonestoblenderformat', icon='OUTLINER_OB_ARMATURE')
            box.operator('object.convertbonestoseformat', icon='OUTLINER_DATA_ARMATURE')
