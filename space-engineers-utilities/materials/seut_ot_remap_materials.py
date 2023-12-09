import bpy
import os

from bpy.types              import Operator

from ..seut_errors          import get_abs_path, seut_report
from ..seut_utils           import get_preferences, prep_context, get_seut_blend_data


class SEUT_OT_RemapMaterials(Operator):
    """Remap materials of objects in the current scene to asset library materials wherever possible"""
    bl_idname = "object.remapmaterials"
    bl_label = "Remap Materials"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        data = get_seut_blend_data()
        return remap_materials(self, context, data.seut.remap_all)

    

# The original version of this code was written by Kamikaze
def remap_materials(self, context, all_objects = False):
    """Remap materials of objects in all scenes to linked asset materials"""

    scene = context.scene
    preferences = get_preferences()
    current_scene = context.window.scene
    current_area = prep_context(context)
    data = get_seut_blend_data()

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

    for file in blends:
        with bpy.data.libraries.load(os.path.join(materials_path, file), link=True) as (data_from, data_to):
            data_to.materials = data_from.materials

    if all_objects:
        objs = bpy.data.objects
    else:
        objs = context.view_layer.objects

    for obj in objs:
        if obj.type != 'MESH':
            continue
        
        parent_lc = None
        for lc in scene.view_layers['SEUT'].layer_collection.children[f"SEUT ({scene.seut.subtypeId})"].children:
            if obj.name in lc.collection.objects:
                parent_lc = lc
                break
            
        try:
            context.view_layer.objects.active = obj

            if parent_lc is not None:
                hide = parent_lc.hide_viewport
                parent_lc.hide_viewport = False

            obj.select_set(True)

            bpy.ops.object.material_slot_remove_unused()

            obj.select_set(False)

            if parent_lc is not None:
                parent_lc.hide_viewport = hide

        except Exception as e:
            print(e)
            seut_report(self, context, 'WARNING', True, 'W003', obj.name)


        for slot in obj.material_slots:
            if slot.material is not None and slot.material.library is None:
                if slot.material.name == "SEUT Material":
                    continue
                old_material = slot.material
                new_material = None

                if old_material.name[:-4] in bpy.data.materials:
                    new_material = old_material.name[:-4]
                else:
                    new_material = old_material.name
                
                if data.seut.fix_scratched_materials and new_material is not None and "Scratched_" in new_material and new_material.replace("Scratched", "") in bpy.data.materials:
                    new_material = new_material.replace("Scratched", "")

                if new_material is not None:
                    for mat in bpy.data.materials:
                        if mat.name == new_material:
                            slot.material = mat

    for mat in bpy.data.materials:
        if mat is not None and mat.library is not None and mat.users < 1:
            bpy.data.materials.remove(mat, do_unlink=True)
    
    for img in bpy.data.images:
        if img is not None and img.library is not None and img.users < 1:
            bpy.data.images.remove(img, do_unlink=True)
            
    for ng in bpy.data.node_groups:
        if ng is not None and ng.library is not None and ng.users < 1:
            bpy.data.node_groups.remove(ng, do_unlink=True)

    context.area.type = current_area
    context.window.scene = current_scene

    return {'FINISHED'}