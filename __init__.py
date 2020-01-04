bl_info = {
    "name": "Space Engineers Utilities",
    "description": "This addon offers various utilities to make creating assets for Space Engineers easier.",
    "author": "Kamikaze, enenra",
    "version": (0, 1, 0),
    "blender": (2, 81, 0),
    "location": "View3D > Tools ",
    "warning": "",
    "wiki_url": "https://github.com/enenra/space-engineers-utilities",
    "tracker_url": "https://github.com/enenra/space-engineers-utilities/issues",
    "support": "COMMUNITY",
    "category": "Scene"
}

# TODO: Write this

import bpy

class RemapLibraryMaterials(bpy.types.Operator):
    """Cleans the materials of an imported Space Engineers FBX and assigns the materials from the MatLibs."""
    bl_idname = "object.remap_library_materials"
    bl_label = "Remap Materials"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        # The original script
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
            bpy.data.materials.remove(mtl, do_unlink=True, do_id_user=True, do_ui_user=False)

        bpy.context.view_layer.objects.active = active

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(RemapLibraryMaterials.bl_idname)


addon_keymaps = []


def register():
    bpy.utils.register_class(RemapLibraryMaterials)
    bpy.types.VIEW3D_MT_object.append(menu_func)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new(RemapLibraryMaterials.bl_idname, 'L', 'PRESS', ctrl=True, alt=True)
        addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(RemapLibraryMaterials)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()