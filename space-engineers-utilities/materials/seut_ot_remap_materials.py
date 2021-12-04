import bpy
import os

from bpy.types              import Operator

from ..seut_errors          import get_abs_path, seut_report
from ..seut_utils           import get_preferences, prep_context


class SEUT_OT_RemapMaterials(Operator):
    """Remap materials of objects in all scenes to linked library materials"""
    bl_idname = "object.remapmaterials"
    bl_label = "Remap Materials"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        return remap_materials(self, context)

    

# The original version of this code was written by Kamikaze
def remap_materials(self, context):
    """Remap materials of objects in all scenes to linked asset materials"""

    preferences = get_preferences()
    current_scene = context.window.scene
    current_area = prep_context(context)

    materials_path = os.path.join(get_abs_path(preferences.asset_path), 'Materials')
    if not os.path.exists(materials_path):
        seut_report(self, context, 'ERROR', True, 'E012', "Asset Directory", get_abs_path(preferences.asset_path))
        return {'CANCELLED'}

    blends = []
    for file in os.listdir(materials_path):
        if file is not None and file.endswith(".blend"):
            blends.append(file)

    if blends == []:
        seut_report(self, context, 'ERROR', True, 'E021', materials_path)
        return {'CANCELLED'}

    available_mats = {}
    for file in blends:
        with bpy.data.libraries.load(os.path.join(materials_path, file), link=True) as (data_from, data_to):
            data_to.materials = data_from.materials

        for mat in data_to.materials:
            if mat.asset_data is not None:
                available_mats[mat.name] = file
            if mat is not None and mat.users < 1:
                bpy.data.materials.remove(mat, do_unlink=True)
        
        for img in data_from.images:
            if img is not None and img in bpy.data.images:
                img = bpy.data.images[img]
                if img.users < 1:
                    bpy.data.images.remove(img, do_unlink=True)
                
        for ng in data_from.node_groups:
            if ng is not None and ng in bpy.data.node_groups:
                ng = bpy.data.node_groups[ng]
                if ng.users < 1:
                    bpy.data.node_groups.remove(ng, do_unlink=True)
    
    if available_mats == {}:
        seut_report(self, context, 'ERROR', True, 'E026', materials_path)
        return {'FINISHED'}

    for scn in bpy.data.scenes:
        context.window.scene = scn

        for obj in context.view_layer.objects:
            if obj.type != 'MESH':
                continue

            context.view_layer.objects.active = obj

            try:
                bpy.ops.object.material_slot_remove_unused()
            except RuntimeError:
                seut_report(self, context, 'WARNING', True, 'W003', obj.name)

            for slot in obj.material_slots:
                if slot.material is not None and slot.material.library is None:
                    old_material = slot.material
                    new_material = None

                    if old_material.name in available_mats:
                        new_material = old_material.name
                    elif old_material.name[:-4] in available_mats:
                        new_material = old_material.name[:-4]

                    if new_material is not None:
                        with bpy.data.libraries.load(os.path.join(materials_path, available_mats[new_material]), link=True) as (data_from, data_to):
                            data_to.materials = [name for name in data_from.materials if name == new_material]
                        for mat in bpy.data.materials:
                            if mat is not None and mat.name == new_material and mat.library is not None:
                                slot.material = mat

    context.area.type = current_area
    context.window.scene = current_scene

    return {'FINISHED'}