import bpy

class SEUT_OT_RemapMaterials(bpy.types.Operator):
    """Remap materials on selected object to linked library materials."""
    bl_idname = "object.remapmaterials"
    bl_label = "Remap Materials"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        # Debug
        print('OT: Remap Materials')
        
        # In order to be able to call on this code from the import operator as well, the target object needs to be passed to the function doing the remapping.
        # object.remapmaterials will always execute on the selected object, but import will need to run the function below on the importer object.
        target = bpy.context.view_layer.objects.active
        SEUT_OT_RemapMaterials.remap_To_Library_Materials(context, target)


        return {'FINISHED'}
        
    # This code was written by Kamikaze
    # ========== TODO ========== 
    # Change this to use a passed object, and not the selected one, then pass the selected object to it when execute is called for just remap
    def remap_To_Library_Materials(context, target):

        # The original script
        mtl_to_delete = []
        active = target

        # For each selected object
        for obj in bpy.context.view_layer.objects.selected:
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
                        if mtl.library != None and mtl.name == old_material.name:
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

        bpy.context.view_layer.objects.active = active
