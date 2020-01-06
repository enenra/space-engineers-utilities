import bpy

class SEUT_OT_RemapMaterials(bpy.types.Operator):
    """Remap materials of the active object to linked library materials"""
    bl_idname = "object.remapmaterials"
    bl_label = "Remap Materials"
    bl_options = {'REGISTER', 'UNDO'}

    # Greys the button out if there is no active object.
    @classmethod
    def poll(cls, context):
        return context.view_layer.objects.active is not None

    def execute(self, context):
        
        target = bpy.context.view_layer.objects.active
        SEUT_OT_RemapMaterials.remap_To_Library_Materials(context, target)


        return {'FINISHED'}
        
    # This code was written by Kamikaze
    # It currently doesn't care too much about the passed target, always uses the current active object.
    # But that doesn't matter much because the only place elsewhere I use it is after import, which sets imported objects as active.
    def remap_To_Library_Materials(context, target):

        print("SEUT Info: Remapping materials.")

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

                    print("SEUT Info: Material '" + slot.material.name + "' not found in linked MatLibs.")

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
    
        return