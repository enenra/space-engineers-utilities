import bpy

from bpy.types              import Operator

from ..seut_errors          import seut_report
from ..seut_utils           import prep_context


class SEUT_OT_RemapMaterials(Operator):
    """Remap materials of objects in all scenes to linked library materials"""
    bl_idname = "object.remapmaterials"
    bl_label = "Remap Materials"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        scene = context.scene
        wm = context.window_manager

        return
        enabled = False
        for lib in wm.seut.matlibs:
            if lib.enabled:
                enabled = True
                break
        
        if enabled:
            result = remap_materials(self, context)
            return result
        else:
            seut_report(self, context, 'ERROR', True, 'E042')
            return {'CANCELLED'}

    

# The original version of this code was written by Kamikaze
def remap_materials(self, context):
    """Remap materials of objects in all scenes to linked library materials"""

    current_scene = context.window.scene
    current_area = prep_context(context)
    
    mtl_to_delete = []

    for scn in bpy.data.scenes:
        context.window.scene = scn

        for obj in context.view_layer.objects:

            if obj.type != 'MESH':
                continue

            # Select this object and remove any unused materials
            context.view_layer.objects.active = obj

            try:
                bpy.ops.object.material_slot_remove_unused()
            except RuntimeError:
                seut_report(self, context, 'WARNING', True, 'W003', obj.name)

            for slot in obj.material_slots:
                if slot.material != None and slot.material.library == None:
                    # This material is not linked from a library
                    old_material = slot.material

                    new_material = None
                    # Try to find a linked material with the same name
                    for mtl in bpy.data.materials:
                        # If an object is imported that has a material that already exists in the scene, it is numbered.
                        # Thus checking the substring of the name is necessary to catch all of them.
                        if mtl.library != None and ( mtl.name == old_material.name or mtl.name == old_material.name[:-4] ) and old_material.seut.overrideMatLib == False:
                            new_material = mtl
                            break                            

                    if new_material != None:
                        # Use the linked material
                        slot.material = new_material
                        # Delete the old material
                        if old_material not in mtl_to_delete:
                            mtl_to_delete.append(old_material)

    for mtl in mtl_to_delete:
        bpy.data.materials.remove(
            mtl, do_unlink=True, do_id_user=True, do_ui_user=False)

    context.area.type = current_area
    context.window.scene = current_scene

    return {'FINISHED'}