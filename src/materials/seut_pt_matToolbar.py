import bpy

from bpy.types      import Panel


class SEUT_PT_Panel_Materials(Panel):
    """Creates the materials panel for SEUT"""
    bl_idname = "SEUT_PT_Panel_Materials"
    bl_label = "Space Engineers Utilities"
    bl_category = "SEUT"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        scene = context.scene

        if bpy.context.active_object is not None and bpy.context.active_object.active_material is not None:

            material = bpy.context.active_object.active_material

            box = layout.box()
            split = box.split(factor=0.85)
            split.label(text=material.name, icon_value=layout.icon(material))
            link = split.operator('wm.semref_link', text="", icon='INFO')
            link.section = 'reference'
            link.page = 'shader-editor-panel'

            if material.node_tree is not None and material.node_tree.nodes is not None:
                for node in material.node_tree.nodes:
                    if node.name == "SEUT_MAT" and node.node_tree is not None:
                        box.label(text="Preset: " + node.node_tree.name)
                        break

            box.prop(material.seut, 'overrideMatLib')
            box.prop(material.seut, 'technique', icon='IMGDISPLAY')
            box.prop(material.seut, 'facing')
            
            box.prop(material.seut, 'windScale', icon='SORTSIZE')
            box.prop(material.seut, 'windFrequency', icon='GROUP')

        box = layout.box()

        split = box.split(factor=0.85)
        split.label(text="Create SEUT Material", icon='MATERIAL')
        link = split.operator('wm.semref_link', text="", icon='INFO')
        link.section = 'tutorials'
        link.page = 'create-material'

        box.prop(wm.seut, 'matPreset', icon='PRESET')
        box.operator('object.mat_create', icon='ADD')

class SEUT_PT_Panel_MatLib(Panel):
    """Creates the MatLib linking panel for SEUT"""
    bl_idname = "SEUT_PT_Panel_MatLib"
    bl_label = "Material Libraries"
    bl_category = "SEUT"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        scene = context.scene
        
        rows = 2
        row = layout.row()
        row.template_list('SEUT_UL_MatLib', "", wm.seut , 'matlibs', wm.seut , 'matlib_index', rows=rows)
        layout.operator('scene.refresh_matlibs', icon='FILE_REFRESH')
        
        layout.separator()
        split = layout.split(factor=0.85)
        split.operator('scene.export_materials', icon='EXPORT')
        link = split.operator('wm.semref_link', text="", icon='INFO')
        link.section = 'tutorials'
        link.page = 'create-matlib'