import bpy
import addon_utils

from bpy.types  import Panel

from .seut_collections              import get_collections


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
        
        if addon_utils.check('blender_addon_updater') == (True, True) and __package__ in wm.bau.addons:
            bau_entry = wm.bau.addons[__package__]
            if not bau_entry.dev_mode and bau_entry.rel_ver_needs_update or bau_entry.dev_mode and bau_entry.rel_ver_needs_update:
                row = layout.row()
                row.alert = True
                row.label(text="SEUT Update Available", icon='ERROR')
                row = layout.row()
                row.label(text="Go to Preferences to update.")

        elif wm.seut.needs_update:
            row = layout.row()
            row.alert = True
            row.label(text=wm.seut.update_message, icon='ERROR')
            row.operator('wm.get_update', icon='IMPORT', text="")

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

            # SubtypeId
            box = layout.box()
            split = box.split(factor=0.85)
            split.label(text=scene.name, icon_value=layout.icon(scene))
            link = split.operator('wm.semref_link', text="", icon='INFO')
            link.section = 'reference/'
            link.page = 'main-panel'

            box.prop(scene.seut, 'sceneType')
            if scene.seut.sceneType == 'mainScene' or scene.seut.sceneType == 'subpart':
                box.prop(scene.seut,'linkSubpartInstances')
            
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
                        
            layout.prop(wm.seut, 'simpleNavigationToggle')

            row = layout.row()
            if wm.seut.issue_alert:
                row.alert = True
            row.operator('wm.issue_display', icon='INFO')


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
        return (scene.seut.sceneType == 'mainScene' or scene.seut.sceneType == 'subpart' or scene.seut.sceneType == 'character') and 'SEUT' in scene.view_layers


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        wm = context.window_manager

        split = layout.split(factor=0.85)
        split.operator('scene.recreate_collections', icon='COLLECTION_NEW')
        link = split.operator('wm.semref_link', text="", icon='INFO')
        link.section = 'reference/'
        link.page = 'outliner'

        layout.operator('scene.create_collection')

        active_col = context.view_layer.active_layer_collection.collection

        if active_col.seut.col_type == 'lod' or active_col.seut.col_type == 'bs_lod' or active_col.seut.col_type == 'hkt' or active_col.seut.col_type == 'bs_lod':
            box = layout.box()
            box.label(text='Options', icon='SETTINGS')

            if active_col.seut.col_type == 'lod' or active_col.seut.col_type == 'bs_lod':
                box.prop(active_col.seut,'lod_distance')

            if active_col.seut.col_type == 'hkt':
                split = box.split(factor=0.40)
                col = split.column()
                col.label(text="Reference:")
                col = split.column()
                col.prop(active_col.seut,'ref_col', text="")


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
        return scene.seut.sceneType == 'mainScene' and 'SEUT' in scene.view_layers


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        wm = context.window_manager

        # Toggle
        layout.prop(wm.seut,'bBoxToggle', expand=True)

        if wm.seut.bBoxToggle == 'on':
            # Size
            box = layout.box()
            box.label(text="Size", icon='PIVOT_BOUNDBOX')
            row = box.row()
            row.prop(scene.seut, "bBox_X")
            row.prop(scene.seut, "bBox_Y")
            row.prop(scene.seut, "bBox_Z")

            row = box.row()
            row.prop(wm.seut, 'bboxColor', text="")
            
            row = box.row()
            row.operator('object.bbox_auto', icon='AUTO')


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
        return scene.seut.sceneType == 'mainScene' and 'SEUT' in scene.view_layers


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        wm = context.window_manager

        if scene.seut.mirroringToggle == 'on':
            split = layout.split(factor=0.85)
            row = split.row()
            row.prop(scene.seut, 'mirroringToggle', expand=True)
            link = split.operator('wm.semref_link', text="", icon='INFO')
            link.section = 'tutorials/'
            link.page = 'mirroring'
            
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
        return scene.seut.sceneType == 'mainScene' and 'SEUT' in scene.view_layers


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        wm = context.window_manager

        if scene.seut.mountpointToggle == 'on':
            split = layout.split(factor=0.85)
            row = split.row()
            row.prop(scene.seut, 'mountpointToggle', expand=True)
            link = split.operator('wm.semref_link', text="", icon='INFO')
            link.section = 'tutorials/'
            link.page = 'mountpoints'

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
        return scene.seut.sceneType == 'mainScene' and 'SEUT' in scene.view_layers


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        wm = context.window_manager
        
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
            box.label(text='Options', icon='SETTINGS')
            box.prop(scene.seut, 'renderColorOverlay', invert_checkbox=True)
            box.prop(scene.seut, 'renderResolution')
            box.prop(scene.render.image_settings, 'file_format')
            
            split = box.split(factor=0.85)
            col = split.column()
            col.prop(scene.render, 'filepath', text="Folder", expand=True)
            col = split.column()
            col.operator('scene.copy_render_options', text="", icon='PASTEDOWN')


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
        return (scene.seut.sceneType == 'mainScene' or scene.seut.sceneType == 'subpart' or scene.seut.sceneType == 'character' or scene.seut.sceneType == 'character_animation') and 'SEUT' in scene.view_layers


    def draw(self, context):
        layout = self.layout
        scene = context.scene

        collections = get_collections(scene)

        # Export
        row = layout.row()
        row.scale_y = 2.0
        row.operator('scene.export_all_scenes', icon='EXPORT')
        row = layout.row()
        row.scale_y = 1.1
        row.operator('scene.export', icon='EXPORT')

        # Options
        box = layout.box()
        box.label(text="Options", icon='SETTINGS')
    
        row = box.row()
        split = box.split(factor=0.70)
        col = split.column()
        col.prop(scene.seut, "export_deleteLooseFiles")
        col = split.column()
        col.prop(scene.seut, "export_sbc")

        if scene.seut.sceneType != 'character' and scene.seut.sceneType != 'character_anmiation':
            box2 = box.box()
            box2.label(text="Grid Export", icon='GRID')
            split = box2.split(factor=0.5)
            col = split.column(align=True)
            col.prop(scene.seut, "export_largeGrid", icon='MESH_CUBE')
            col = split.column(align=True)
            col.prop(scene.seut, "export_smallGrid", icon='META_CUBE')
            if scene.seut.export_smallGrid and scene.seut.export_largeGrid:
                col.prop(scene.seut, "export_medium_grid", icon='CUBE')
        
        box.prop(scene.seut, "mod_path", text="Mod")
        split = box.split(factor=0.85)
        col = split.column()
        col.prop(scene.seut, "export_exportPath", text="Model")
        col = split.column()
        col.operator('scene.copy_export_options', text="", icon='PASTEDOWN')


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
        return (scene.seut.sceneType == 'mainScene' or scene.seut.sceneType == 'subpart' or scene.seut.sceneType == 'character' or scene.seut.sceneType == 'character_animation') and 'SEUT' in scene.view_layers


    def draw(self, context):

        scene = context.scene
        wm = context.window_manager
        layout = self.layout

        # Import

        row = layout.row()
        row.scale_y = 2.0
        row.operator('scene.import', icon='IMPORT')

        layout.operator('scene.import_complete', icon='IMPORT')
        
        box = layout.box()
        box.label(text='Options', icon='SETTINGS')

        if addon_utils.check("better_fbx") == (True, True):
            box.prop(wm.seut, 'better_fbx', icon='CHECKMARK')

        box.prop(wm.seut, 'fix_scratched_materials', icon='MATERIAL')

        # Repair
        box = layout.box()
        box.label(text="Repair", icon='TOOL_SETTINGS')
        box.operator('object.remapmaterials', icon='MATERIAL')
        box.operator('wm.convert_structure', icon='OUTLINER')
        box.operator('object.fix_positioning', icon='EMPTY_AXIS')

        if scene.seut.sceneType == 'character' or scene.seut.sceneType == 'character_animation':
            # Bones
            box = layout.box()
            box.label(text="Bone Conversion", icon='ARMATURE_DATA')
            box.operator('object.convertbonestoblenderformat', icon='OUTLINER_OB_ARMATURE')
            box.operator('object.convertbonestoseformat', icon='OUTLINER_DATA_ARMATURE')
