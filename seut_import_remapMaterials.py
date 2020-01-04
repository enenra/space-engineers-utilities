import bpy

class SEUT_OT_RemapMaterials(bpy.types.Operator):
    """Remap materials on object to linked library materials."""
    bl_idname = "object.remapmaterials"
    bl_label = "Remap Materials"
    bl_options = {'REGISTER', 'UNDO'}

    # This code was entirely written by Kamikaze
    # ========== TODO ========== 
    # Change this to use a passed object, and not the selected one, then pass the selected object to it when execute is called for just remap
    def execute(self, context):

        # Debug
        print('OT: Remap Materials')

        mtl_to_delete = []
        active = bpy.context.view_layer.objects.active

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

        return {'FINISHED'}
