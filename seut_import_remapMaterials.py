import bpy

class SEUT_OT_RemapMaterials(bpy.types.Operator):
    """Remap materials of the active object to linked library materials"""
    bl_idname = "object.remapmaterials"
    bl_label = "Remap Materials"
    bl_options = {'REGISTER', 'UNDO'}

    # Greys the button out if there is no active object.
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) != 0

    # ========== TODO ==========
    # Need to rewrite this so that when you import a second object after the first one, the shared textures aren't pink.

    # This code was written by Kamikaze
    def execute(self, context):

        print("SEUT Info: Remapping materials.")
        
        mtl_to_delete = []

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

        return {'FINISHED'}