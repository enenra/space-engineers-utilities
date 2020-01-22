import bpy


class SEUT_PT_Panel_Materials(bpy.types.Panel):
    """Creates the materials panel for SEUT"""
    bl_idname = "SEUT_PT_Panel_Materials"
    bl_label = "Space Engineers Utilities"
    bl_category = "SEUT"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        if bpy.context.active_object.active_material != None:

            material = bpy.context.active_object.active_material

            box = layout.box()
            box.label(text=material.name, icon_value=layout.icon(material))

            for node in material.node_tree.nodes:
                if node.name == "SEUT_MAT":
                    box.label(text="Preset: " + node.node_tree.name)
                    break

            box.prop(material.seut, 'overrideMatLib')
            box.prop(material.seut, 'technique')

            if material.seut.technique == 'GLASS' or material.seut.technique == 'ALPHA_MASKED':
                boxSpec = box.box()
                boxSpec.label(text="Specularity")
                boxSpec.prop(material.seut, 'specularIntensity')
                boxSpec.prop(material.seut, 'specularPower')

                boxDiff = box.box()
                boxDiff.prop(material.seut, 'diffuseColor', text="Diffuse Color")

        box = layout.box()
        box.label(text="Create new SEUT Material")
        box.prop(scene.seut, 'matPreset', text="Preset")
        box.operator('object.mat_create')