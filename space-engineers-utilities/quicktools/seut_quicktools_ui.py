import bpy
import json

from bpy.types  import Panel, UIList
from distutils.fancy_getopt import wrap_text

from ..utils.seut_patch_blend       import check_patch_needed
from ..seut_collections             import get_collections
from ..seut_utils                   import get_seut_blend_data, get_preferences


class SEUT_PT_Panel_QuickTools(Panel):
    """Creates the Quick Tools menu"""
    bl_idname = "SEUT_PT_Panel_QuickTools"
    bl_label = "Quick Tools"
    bl_category = "SEUT"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return 'SEUT' in scene.view_layers and not check_patch_needed() and context.area.type == 'VIEW_3D' and get_preferences().quick_tools


    def draw(self, context):
        scene = context.scene
        data = get_seut_blend_data()
        collections = get_collections(scene)
        active_object = context.active_object
        layout = self.layout

        active_col = context.view_layer.active_layer_collection.collection

        current_space = None
        for area in context.screen.areas:
            if area.type != 'VIEW_3D':
                continue
            for space in area.spaces:
                if space.type != 'VIEW_3D':
                    continue
                current_space = space
                break

        if active_col.seut.col_type == 'main':
            box = layout.box()
            box.label(text="Main", icon='COLLECTION_COLOR_04')
            box.operator("quicktools.add_bevels", icon='MOD_BEVEL')

        elif active_col.seut.col_type == 'hkt':
            box = layout.box()
            box.label(text="Collision", icon='COLLECTION_COLOR_08')
            box.operator("quicktools.apply_transforms", icon='CHECKBOX_HLT')

        elif active_col.seut.col_type == 'bs':
            box = layout.box()
            box.label(text="Build Stage", icon='COLLECTION_COLOR_05')
            box.operator("quicktools.apply_construction_material", text="Apply 'Construction'", icon='MATERIAL')
            box.operator("quicktools.cut_and_solidify", icon='MOD_SOLIDIFY')

        elif active_col.seut.col_type == 'lod':
            box = layout.box()

            if active_col.seut.ref_col.seut.col_type == 'bs':
                box.label(text="Level of Detail", icon='COLLECTION_COLOR_06')
            else:
                box.label(text="Level of Detail", icon='COLLECTION_COLOR_01')

            box.operator("quicktools.remove_bevels", icon='MOD_BEVEL')
            box.prop(data.seut, "qt_lod_view", icon='VIEW_CAMERA')
            

        if active_object is not None and context.active_object.mode == 'EDIT':
            box = layout.box()
            box.label(text="Edit Mode", icon='EDITMODE_HLT')
            
            # Face Orientation
            col = box.column(align=True)
            col.prop(current_space.overlay, "show_face_orientation", icon='NORMALS_FACE')
            row = col.row(align=True)
            row.operator("mesh.flip_normals")
            op = row.operator("mesh.normals_make_consistent", text="Recalculate Outside")
            op.inside = False

            # Origin
            col = box.column(align=True)
            row = col.row(align=True)
            op = row.operator("quicktools.origin_to_selected", icon='TRANSFORM_ORIGINS')
            

        elif active_object is not None and context.active_object.mode == 'OBJECT':
            box = layout.box()
            box.label(text="Object Mode", icon='OBJECT_DATAMODE')
            
            box.prop(current_space.overlay, "show_face_orientation", icon='NORMALS_FACE')

            op = box.operator("object.origin_set", text="Origin to Geometry", icon='TRANSFORM_ORIGINS')
            op.type = 'ORIGIN_GEOMETRY'

            box.operator("quicktools.mirror_apply", icon='MOD_MIRROR')