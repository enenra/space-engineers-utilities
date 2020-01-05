import bpy

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

        box = layout.box()
        box.label(text="Grid Scale")
        row = box.row()
        row.prop(scene,'prop_gridScale', expand=True)
        
        layout.operator('object.recreate_collections', text="Recreate Collections")


class SEUT_PT_Panel_BoundingBox(bpy.types.Panel):
    """Creates the bounding box panel for SEUT"""
    bl_idname = "SEUT_PT_Panel_BoundingBox"
    bl_label = "Bounding Box"
    bl_category = "SEUT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Toggle
        layout.prop(scene,'prop_bBoxToggle', expand=True)

        # Size
        box = layout.box()
        box.label(text="Size")
        row = box.row()
        row.prop(scene, "prop_bBox_X")
        row.prop(scene, "prop_bBox_Y")
        row.prop(scene, "prop_bBox_Z")

        # ========== TODO ==========
        # Add "Automatic"-button to dynamically adjust the box depending on object size.

class SEUT_PT_Panel_Export(bpy.types.Panel):
    """Creates the export panel for SEUT"""
    bl_idname = "SEUT_PT_Panel_Export"
    bl_label = "Export"
    bl_category = "SEUT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Export
        row = layout.row()
        row.scale_y = 2.0
        row.operator('object.export', text="Export")
        
        # Partial
        box = layout.box()
        box.label(text="Partial Export")
        split = box.split()
        
        col = split.column()
        col.operator('object.export_main', text="Main")
        col.operator('object.export_lod', text="LODs")

        col = split.column(align=True)
        col.operator('object.export_bs', text="Build Stages")
        col.operator('object.export_hkt', text="Collision")

        # Options
        box = layout.box()
        box.label(text="Options")
        split = box.split()
        
        col = split.column()
        col.prop(scene, "prop_export_fbx")

        col = split.column(align=True)
        col.prop(scene, "prop_export_xml")
        
        col = split.column(align=True)
        col.prop(scene, "prop_export_sbc")

        box.prop(scene, "prop_export_rescaleFactor")

        # SubtypeId
        box = layout.box()
        box.label(text="SubtypeId")
        box.prop(scene, 'prop_subtypeId', text='', expand=True)
        
        # LOD
        box = layout.box()
        box.label(text="LOD Distance")
        box.prop(scene, "prop_export_lod1Distance")
        box.prop(scene, "prop_export_lod2Distance")
        box.prop(scene, "prop_export_lod3Distance")


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
        box.operator('object.remapmaterials', text="Remap Materials")