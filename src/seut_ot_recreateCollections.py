import bpy
import re

from bpy.types import Operator

class SEUT_OT_RecreateCollections(Operator):
    """Recreates the collections"""
    bl_idname = "object.recreate_collections"
    bl_label = "Recreate Collections"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        SEUT_OT_RecreateCollections.create_Collections(context)

        return {'FINISHED'}


    def getCollections(scene):
        """Scans existing collections to find the SEUT ones"""

        if not 'SEUT' in scene.view_layers:
            # This errors sometimes if it's triggered from draw in the toolbar
            try:
                scene.view_layers[0].name = 'SEUT'
            except:
                pass

        tag = ' (' + scene.seut.subtypeId + ')'

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

        children = scene.view_layers['SEUT'].layer_collection.children

        if str('SEUT' + tag) in children:
            collections['seut'] = children['SEUT' + tag].collection

        if not collections['seut'] is None:
            for col in collections['seut'].children:

                if col.name == 'Main' + tag:
                    collections['main'] = col

                if col.name == 'Collision' + tag:
                    collections['hkt'] = col

                elif col.name == 'LOD1' + tag:
                    collections['lod1'] = col

                elif col.name == 'LOD2' + tag:
                    collections['lod2'] = col

                elif col.name == 'LOD3' + tag:
                    collections['lod3'] = col

                elif col.name == 'BS1' + tag:
                    collections['bs1'] = col

                elif col.name == 'BS2' + tag:
                    collections['bs2'] = col
                    
                elif col.name == 'BS3' + tag:
                    collections['bs3'] = col
                    
                elif col.name == 'BS_LOD' + tag:
                    collections['bs_lod'] = col
        
        return collections


    def rename_Collections(scene):
        """Scans existing collections to find the SEUT ones and renames them if the tag has changed"""

        if not 'SEUT' in scene.view_layers:
            scene.view_layers[0].name = 'SEUT'

        tag = ' (' + scene.seut.subtypeId + ')'
        tagOld = ' (' + scene.seut.subtypeBefore + ')'

        children = scene.view_layers['SEUT'].layer_collection.children

        for main in children:
            if main.collection.name == 'SEUT' + tagOld or main.collection.name[:4 + len(tagOld)] == 'SEUT' + tagOld and re.search("\.[0-9]{3}", main.collection.name[-4:]) != None:
                mainCollection = main.collection
                main.collection.name = 'SEUT' + tag
        
        if mainCollection is None:
            return

        for col in mainCollection.children:
            if col.name[:6] == 'Main (':
                col.name = 'Main' + tag
                
            elif col.name[:11] == 'Collision (':
                col.name = 'Collision' + tag
                
            elif col.name[:11] == 'Mirroring (':
                col.name = 'Mirroring' + tag
                
            elif col.name[:13] == 'Mountpoints (':
                col.name = 'Mountpoints' + tag
                
            elif col.name[:8] == 'Render (':
                col.name = 'Render' + tag
                
            elif col.name[:6] == 'LOD1 (':
                col.name = 'LOD1' + tag
                
            elif col.name[:6] == 'LOD2 (':
                col.name = 'LOD2' + tag
                
            elif col.name[:6] == 'LOD3 (':
                col.name = 'LOD3' + tag
                
            elif col.name[:5] == 'BS1 (':
                col.name = 'BS1' + tag
                
            elif col.name[:5] == 'BS2 (':
                col.name = 'BS2' + tag
                
            elif col.name[:5] == 'BS3 (':
                col.name = 'BS3' + tag
                
            elif col.name[:8] == 'BS_LOD (':
                col.name = 'BS_LOD' + tag

        return


    def create_Collections(context):
        """Recreates the collections SEUT requires"""

        scene = context.scene

        if not 'SEUT' in scene.view_layers:
            scene.view_layers[0].name = 'SEUT'

        if scene.seut.subtypeId == "":
            scene.seut.subtypeId = scene.name
            scene.seut.subtypeBefore = scene.name
            
        tag = ' (' + scene.seut.subtypeId + ')'

        collections = SEUT_OT_RecreateCollections.getCollections(scene)

        if collections['seut'] == None:
            collections['seut'] = bpy.data.collections.new('SEUT' + tag)
            scene.collection.children.link(collections['seut'])

        if collections['main'] == None:
            collections['main'] = bpy.data.collections.new('Main' + tag)
            collections['seut'].children.link(collections['main'])

        if collections['hkt'] == None:
            collections['hkt'] = bpy.data.collections.new('Collision' + tag)
            collections['seut'].children.link(collections['hkt'])

        if collections['bs1'] == None:
            collections['bs1'] = bpy.data.collections.new('BS1' + tag)
            collections['seut'].children.link(collections['bs1'])

        if collections['bs2'] == None:
            collections['bs2'] = bpy.data.collections.new('BS2' + tag)
            collections['seut'].children.link(collections['bs2'])

        if collections['bs3'] == None:
            collections['bs3'] = bpy.data.collections.new('BS3' + tag)
            collections['seut'].children.link(collections['bs3'])

        if collections['lod1'] == None:
            collections['lod1'] = bpy.data.collections.new('LOD1' + tag)
            collections['seut'].children.link(collections['lod1'])

        if collections['lod2'] == None:
            collections['lod2'] = bpy.data.collections.new('LOD2' + tag)
            collections['seut'].children.link(collections['lod2'])

        if collections['lod3'] == None:
            collections['lod3'] = bpy.data.collections.new('LOD3' + tag)
            collections['seut'].children.link(collections['lod3'])

        if collections['bs_lod'] == None:
            collections['bs_lod'] = bpy.data.collections.new('BS_LOD' + tag)
            collections['seut'].children.link(collections['bs_lod'])

        return collections