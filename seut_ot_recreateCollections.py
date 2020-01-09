import bpy

class SEUT_OT_RecreateCollections(bpy.types.Operator):
    """Recreates the collections"""
    bl_idname = "object.recreate_collections"
    bl_label = "Recreate Collections"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        SEUT_OT_RecreateCollections.create_Collections(context)

        return {'FINISHED'}


    def get_Collections():
        """Scans existing collections to find the SEUT ones"""

        collections = {
            'seut': None,
            'main': None,
            'hkt': None,
            'lod1': None,
            'lod2': None,
            'lod3': None,
            'bs1': None,
            'bs2': None,
            'bs3': None,
            }

        if len(bpy.data.collections) > 0:
            for col in bpy.data.collections:
                if col.name == 'SEUT':
                    collections['seut'] = col

                if col.name == 'Main':
                    collections['main'] = col

                if col.name == 'Collision':
                    collections['hkt'] = col

                elif col.name == 'LOD1':
                    collections['lod1'] = col

                elif col.name == 'LOD2':
                    collections['lod2'] = col

                elif col.name == 'LOD3':
                    collections['lod3'] = col

                elif col.name == 'BS1':
                    collections['bs1'] = col

                elif col.name == 'BS2':
                    collections['bs2'] = col
                    
                elif col.name == 'BS3':
                    collections['bs3'] = col
        
        return collections


    def create_Collections(context):
        """Recreates the collections SEUT requires"""

        collections = SEUT_OT_RecreateCollections.get_Collections()

        if collections['seut'] == None:
            collections['seut'] = bpy.data.collections.new('SEUT')
            context.scene.collection.children.link(collections['seut'])

        if collections['main'] == None:
            collections['main'] = bpy.data.collections.new('Main')
            collections['seut'].children.link(collections['main'])

        if collections['hkt'] == None:
            collections['hkt'] = bpy.data.collections.new('Collision')
            collections['seut'].children.link(collections['hkt'])

        if collections['bs1'] == None:
            collections['bs1'] = bpy.data.collections.new('BS1')
            collections['seut'].children.link(collections['bs1'])

        if collections['bs2'] == None:
            collections['bs2'] = bpy.data.collections.new('BS2')
            collections['seut'].children.link(collections['bs2'])

        if collections['bs3'] == None:
            collections['bs3'] = bpy.data.collections.new('BS3')
            collections['seut'].children.link(collections['bs3'])

        if collections['lod1'] == None:
            collections['lod1'] = bpy.data.collections.new('LOD1')
            collections['seut'].children.link(collections['lod1'])

        if collections['lod2'] == None:
            collections['lod2'] = bpy.data.collections.new('LOD2')
            collections['seut'].children.link(collections['lod2'])

        if collections['lod3'] == None:
            collections['lod3'] = bpy.data.collections.new('LOD3')
            collections['seut'].children.link(collections['lod3'])

        return collections