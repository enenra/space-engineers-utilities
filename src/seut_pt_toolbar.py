import bpy

from .seut_ot_recreateCollections  import SEUT_OT_RecreateCollections

class SEUT_PT_Panel(bpy.types.Panel):
    """Creates the topmost panel for SEUT"""
    bl_idname = "SEUT_PT_Panel"
    bl_label = "Space Engineers Utilities"
    bl_category = "SEUT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # SubtypeId
        box = layout.box()
        box.label(text=scene.name, icon_value=layout.icon(scene))
        box.prop(scene.seut, 'sceneType')
        
        box = layout.box()
        box.label(text="SubtypeId")
        box.prop(scene.seut, "subtypeId", text="", expand=True)

        box = layout.box()
        box.label(text="Grid Scale")
        row = box.row()
        row.prop(scene.seut,'gridScale', expand=True)
        
        layout.operator('object.recreate_collections', text="Recreate Collections")


class SEUT_PT_Panel_BoundingBox(bpy.types.Panel):
    """Creates the bounding box panel for SEUT"""
    bl_idname = "SEUT_PT_Panel_BoundingBox"
    bl_label = "Bounding Box"
    bl_category = "SEUT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Toggle
        layout.prop(scene.seut,'bBoxToggle', expand=True)

        # Size
        box = layout.box()
        box.label(text="Size")
        row = box.row()
        row.prop(scene.seut, "bBox_X")
        row.prop(scene.seut, "bBox_Y")
        row.prop(scene.seut, "bBox_Z")
        
        row = box.row()
        row.operator('object.bbox_auto', text="Automatic")

class SEUT_PT_Panel_Export(bpy.types.Panel):
    """Creates the export panel for SEUT"""
    bl_idname = "SEUT_PT_Panel_Export"
    bl_label = "Export"
    bl_category = "SEUT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        collections = SEUT_OT_RecreateCollections.get_Collections(scene)

        # Export
        row = layout.row()
        row.scale_y = 2.0
        row.operator('object.export', text="Export")
        
        """
        # Partial
        box = layout.box()
        box.label(text="Partial Export")
        split = box.split()
        
        col = split.column()
        col.operator('object.export_main', text="Main")
        col.operator('object.export_lod', text="LODs")

        col = split.column()
        col.operator('object.export_buildstages', text="Build Stages")
        col.operator('object.export_hkt', text="Collision")
        """

        # Options
        box = layout.box()
        box.label(text="Options")
        """
        split = box.split()
        col = split.column()
        col.prop(scene.seut, "export_fbx")
        col.prop(scene.seut, "export_sbc")

        col = split.column()
        col.prop(scene.seut, "export_xml")
        col.prop(scene.seut, "export_hkt")
        """
        box.prop(scene.seut, "export_deleteLooseFiles")
        box.prop(scene.seut, "export_rescaleFactor")
        
        box.prop(scene.seut, "export_exportPath", text="Folder", expand=True)
        
        # LOD
        if collections['lod1'] is not None or collections['lod2'] is not None or collections['lod3'] is not None or collections['bs_lod'] is not None:
            box = layout.box()
            box.label(text="LOD Distance")
            if collections['lod1'] is not None:
                box.prop(scene.seut, "export_lod1Distance")
            if collections['lod2'] is not None:
                box.prop(scene.seut, "export_lod2Distance")
            if collections['lod3'] is not None:
                box.prop(scene.seut, "export_lod3Distance")
            if collections['bs_lod'] is not None:
                box.prop(scene.seut, "export_bs_lodDistance")


class SEUT_PT_Panel_Import(bpy.types.Panel):
    """Creates the import panel for SEUT"""
    bl_idname = "SEUT_PT_Panel_Import"
    bl_label = "Import"
    bl_category = "SEUT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout

        # Import
        row = layout.row()
        row.scale_y = 2.0
        row.operator('scene.import', text="Import")

        # Repair
        box = layout.box()
        box.label(text="Repair")
        box.operator('object.emptytocubetype', text="Display Empties as 'Cube'")
        box.operator('object.remapmaterials', text="Remap Materials")
        box.operator('object.structure_conversion', text="Convert to new structure")