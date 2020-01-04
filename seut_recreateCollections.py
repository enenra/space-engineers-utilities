import bpy

class SEUT_OT_RecreateCollections(bpy.types.Operator):
    """Recreates the collections."""
    bl_idname = "object.recreate_collections"
    bl_label = "Recreate Collections"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        # Debug
        print('OT: Recreate Collections')

        # Create a dictionary filled with placeholders for all necessary collections (make this a global prop or dictionary in init?)


        # Loop over existing collections to see whether any already exist. if so, add them to the list.
        # https://blenderartists.org/t/loop-over-collections-in-the-outliner/1172818/4


        # Recreate missing collections and register them to the list

        return {'FINISHED'}