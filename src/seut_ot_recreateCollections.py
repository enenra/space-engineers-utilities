import bpy

from bpy.types import Operator

class SEUT_OT_RecreateCollections(Operator):
    """Recreates the collections"""
    bl_idname = "object.recreate_collections"
    bl_label = "Recreate Collections"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        SEUT_OT_RecreateCollections.create_Collections(context)

        return {'FINISHED'}


    def get_Collections(context):
        """Scans existing collections to find the SEUT ones"""

        scene = context.scene
        sceneIndex = 0
        for index in range(0, len(bpy.data.scenes)):
            if scene == bpy.data.scenes[index]:
                sceneIndex = index

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
            'bs_lod': None,
            }

        if len(bpy.data.collections) > 0:
            for col in bpy.data.collections:
                if col.name == 'SEUT (' + str(index) + ')':
                    collections['seut'] = col

                if col.name == 'Main (' + str(index) + ')':
                    collections['main'] = col

                if col.name == 'Collision (' + str(index) + ')':
                    collections['hkt'] = col

                elif col.name == 'LOD1 (' + str(index) + ')':
                    collections['lod1'] = col

                elif col.name == 'LOD2 (' + str(index) + ')':
                    collections['lod2'] = col

                elif col.name == 'LOD3 (' + str(index) + ')':
                    collections['lod3'] = col

                elif col.name == 'BS1 (' + str(index) + ')':
                    collections['bs1'] = col

                elif col.name == 'BS2 (' + str(index) + ')':
                    collections['bs2'] = col
                    
                elif col.name == 'BS3 (' + str(index) + ')':
                    collections['bs3'] = col
                    
                elif col.name == 'BS_LOD (' + str(index) + ')':
                    collections['bs_lod'] = col
        
        return collections


    def create_Collections(context):
        """Recreates the collections SEUT requires"""

        scene = context.scene
        sceneIndex = 0
        for index in range(0, len(bpy.data.scenes)):
            if scene == bpy.data.scenes[index]:
                sceneIndex = index

        collections = SEUT_OT_RecreateCollections.get_Collections(context)

        if collections['seut'] == None:
            collections['seut'] = bpy.data.collections.new('SEUT (' + str(index) + ')')
            scene.collection.children.link(collections['seut'])

        if collections['main'] == None:
            collections['main'] = bpy.data.collections.new('Main (' + str(index) + ')')
            collections['seut'].children.link(collections['main'])

        if collections['hkt'] == None:
            collections['hkt'] = bpy.data.collections.new('Collision (' + str(index) + ')')
            collections['seut'].children.link(collections['hkt'])

        if collections['bs1'] == None:
            collections['bs1'] = bpy.data.collections.new('BS1 (' + str(index) + ')')
            collections['seut'].children.link(collections['bs1'])

        if collections['bs2'] == None:
            collections['bs2'] = bpy.data.collections.new('BS2 (' + str(index) + ')')
            collections['seut'].children.link(collections['bs2'])

        if collections['bs3'] == None:
            collections['bs3'] = bpy.data.collections.new('BS3 (' + str(index) + ')')
            collections['seut'].children.link(collections['bs3'])

        if collections['lod1'] == None:
            collections['lod1'] = bpy.data.collections.new('LOD1 (' + str(index) + ')')
            collections['seut'].children.link(collections['lod1'])

        if collections['lod2'] == None:
            collections['lod2'] = bpy.data.collections.new('LOD2 (' + str(index) + ')')
            collections['seut'].children.link(collections['lod2'])

        if collections['lod3'] == None:
            collections['lod3'] = bpy.data.collections.new('LOD3 (' + str(index) + ')')
            collections['seut'].children.link(collections['lod3'])

        if collections['bs_lod'] == None:
            collections['bs_lod'] = bpy.data.collections.new('BS_LOD (' + str(index) + ')')
            collections['seut'].children.link(collections['bs_lod'])

        return collections