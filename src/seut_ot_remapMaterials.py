import bpy

from bpy.types                      import Operator

class SEUT_OT_RemapMaterials(Operator):
    """Remap materials of the active object to linked library materials"""
    bl_idname = "object.remapmaterials"
    bl_label = "Remap Materials"
    bl_options = {'REGISTER', 'UNDO'}

    # Greys the button out if there is no selected object.
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) != 0

    # This code was written by Kamikaze
    def execute(self, context):

        self.report({'INFO'}, "SEUT: Remapping local materials to library.")
        
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

        return {'FINISHED'}