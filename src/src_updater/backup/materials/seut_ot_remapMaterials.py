import bpy

from bpy.types                      import Operator

class SEUT_OT_RemapMaterials(Operator):
    """Remap materials of objects in all scenes to linked library materials"""
    bl_idname = "object.remapmaterials"
    bl_label = "Remap Materials"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        print("SEUT Info: Remapping local materials to library.")

        if bpy.context.object is not None and bpy.context.object.mode is not 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        SEUT_OT_RemapMaterials.remapMaterials(self, context)

        return {'FINISHED'}
    
    # This code was written by Kamikaze
    def remapMaterials(self, context):
        """Remap materials of objects in all scenes to linked library materials"""
        
        mtl_to_delete = []

        currentScene = bpy.context.window.scene

        for scene in bpy.data.scenes:
            bpy.context.window.scene = scene

            for obj in bpy.context.view_layer.objects:
                # Select this object and remove any unused materials
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.material_slot_remove_unused()

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

        bpy.context.window.scene = currentScene
        return