import bpy

from bpy.types import Operator

from ..seut_ot_recreateCollections   import SEUT_OT_RecreateCollections
from ..seut_ot_mirroring             import SEUT_OT_Mirroring
from ..seut_utils                    import linkSubpartScene, getParentCollection

class SEUT_OT_StructureConversion(Operator):
    """Ports blend files created with the old plugin to the new structure"""
    bl_idname = "object.structure_conversion"
    bl_label = "Convert to new structure"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        SEUT_OT_StructureConversion.convertToNewStructure(self, context)

        return {'FINISHED'}
    
    def convertToNewStructure(self, context):
        """Converts blend files created with the old plugin to the new structure"""

        # For some reason it breaks if you don't run it starting from the scene at index 0
        currentScene = bpy.context.window.scene
        context.window.scene = bpy.data.scenes[0]

        # Set scene indexes and SubtypeIds
        for scn in bpy.data.scenes:
            scn.seut.subtypeId = scn.name
            tag = ' (' + scn.seut.subtypeId + ')'
            
            # Create main SEUT collection for each scene
            seutExists = False
            for collection in scn.collection.children:
                if collection.name == 'SEUT' + tag:
                    seutExists = True

            if not seutExists:
                scn.view_layers[0].name = 'SEUT'
                seut = bpy.data.collections.new('SEUT' + tag)
                scn.collection.children.link(seut)
            
            # convert collections created from layers to corresponding SEUT collections
            for collection in scn.collection.children:

                if collection.name == 'Collection 1' or collection.name[:13] == 'Collection 1.':
                    if 'Main' + tag in bpy.data.collections:
                        bpy.data.collections.remove(bpy.data.collections['Main' + tag])
                    collection.name = 'Main' + tag
                    
                elif collection.name == 'Collection 2' or collection.name[:13] == 'Collection 2.':
                    if 'Collision' + tag in bpy.data.collections:
                        bpy.data.collections.remove(bpy.data.collections['Collision' + tag])
                    collection.name = 'Collision' + tag
                    
                elif collection.name == 'Collection 3' or collection.name[:13] == 'Collection 3.':
                    if 'Mountpoints' + tag in bpy.data.collections:
                        bpy.data.collections.remove(bpy.data.collections['Mountpoints' + tag])
                    collection.name = 'Mountpoints' + tag
                    
                elif collection.name == 'Collection 4' or collection.name[:13] == 'Collection 4.':
                    if 'Mirroring' + tag in bpy.data.collections:
                        bpy.data.collections.remove(bpy.data.collections['Mirroring' + tag])
                    collection.name = 'Mirroring' + tag
                    
                elif collection.name == 'Collection 6' or collection.name[:13] == 'Collection 6.':
                    if 'LOD1' + tag in bpy.data.collections:
                        bpy.data.collections.remove(bpy.data.collections['LOD1' + tag])
                    collection.name = 'LOD1' + tag
                    
                elif collection.name == 'Collection 7' or collection.name[:13] == 'Collection 7.':
                    if 'LOD2' + tag in bpy.data.collections:
                        bpy.data.collections.remove(bpy.data.collections['LOD2' + tag])
                    collection.name = 'LOD2' + tag
                    
                elif collection.name == 'Collection 8' or collection.name[:13] == 'Collection 8.':
                    if 'LOD3' + tag in bpy.data.collections:
                        bpy.data.collections.remove(bpy.data.collections['LOD3' + tag])
                    collection.name = 'LOD3' + tag
                    
                elif collection.name == 'Collection 11' or collection.name[:14] == 'Collection 11.':
                    if 'BS1' + tag in bpy.data.collections:
                        bpy.data.collections.remove(bpy.data.collections['BS1' + tag])
                    collection.name = 'BS1' + tag
                    
                elif collection.name == 'Collection 12' or collection.name[:14] == 'Collection 12.':
                    if 'BS2' + tag in bpy.data.collections:
                        bpy.data.collections.remove(bpy.data.collections['BS2' + tag])
                    collection.name = 'BS2' + tag
                    
                elif collection.name == 'Collection 13' or collection.name[:14] == 'Collection 13.':
                    if 'BS3' + tag in bpy.data.collections:
                        bpy.data.collections.remove(bpy.data.collections['BS3' + tag])
                    collection.name = 'BS3' + tag
                
                if not collection.name[:4] == 'SEUT':
                    scn.collection.children.unlink(collection)
                    bpy.data.collections['SEUT' + tag].children.link(collection)
                
                collection.hide_viewport = False
                
            # Convert custom properties of empties from harag's to the default blender method.
            for obj in scn.objects:
                if obj.type == 'EMPTY':
                    obj.empty_display_type = 'CUBE'

                    if 'space_engineers' in bpy.data.objects[obj.name] and bpy.data.objects[obj.name]['space_engineers'] is not None:
                        haragProp = bpy.data.objects[obj.name]['space_engineers']

                        targetObjectName = None
                        if haragProp.get('highlight_objects') is not None:
                            customPropName = 'highlight'
                            targetObjectName = haragProp.get('highlight_objects')

                            if targetObjectName in bpy.data.objects:
                                obj.seut.linkedObject = bpy.data.objects[targetObjectName]

                        elif haragProp.get('file') is not None:
                            customPropName = 'file'
                            customPropValue = haragProp.get('file')
                            obj.empty_display_type = 'ARROWS'

                            if customPropValue.find('_Large') != -1:
                                targetObjectName = customPropValue[:customPropValue.find('_Large')]
                            if customPropValue.find('_Small') != -1:
                                targetObjectName = customPropValue[:customPropValue.find('_Small')]
                            else:
                                targetObjectName = customPropValue

                        if targetObjectName is not None:
                            bpy.data.objects[obj.name][customPropName] = targetObjectName
                            del bpy.data.objects[obj.name]['space_engineers']
                            
                            if targetObjectName in bpy.data.scenes:
                                obj.seut.linkedScene = bpy.data.scenes[targetObjectName]
        
            # Convert Mirroring information
            if 'Mirroring' + tag in bpy.data.collections:
                for mirrorEmpty in bpy.data.collections['Mirroring' + tag].objects:
                    if mirrorEmpty.type == 'EMPTY':
                        if mirrorEmpty.name == 'MirrorFrontBack':
                            mirrorEmpty.name = 'Mirroring X'
                            SEUT_OT_Mirroring.saveRotationToProps(self, context, mirrorEmpty)
                        elif mirrorEmpty.name == 'MirrorLeftRight':
                            mirrorEmpty.name = 'Mirroring Y'
                            SEUT_OT_Mirroring.saveRotationToProps(self, context, mirrorEmpty)
                        elif mirrorEmpty.name == 'MirrorTopBottom':
                            mirrorEmpty.name = 'Mirroring Z'
                            SEUT_OT_Mirroring.saveRotationToProps(self, context, mirrorEmpty)
                    
                scn.seut.mirroringToggle = 'off'
            
            # Clean up mountpoints - cannot convert them
            if 'Mountpoints' + tag in bpy.data.collections:
                for mp in bpy.data.collections['Mountpoints' + tag].objects:
                    for child in mp.children:
                        bpy.data.objects.remove(child)
                    mp.select_set(state=False, view_layer=context.window.view_layer)
                    bpy.data.objects.remove(mp)
                bpy.data.collections.remove(bpy.data.collections['Mountpoints' + tag])
        
        bpy.context.window.scene = currentScene

        for scn2 in bpy.data.scenes:
            for emptyObj in scn2.objects:
                if emptyObj.type == 'EMPTY' and 'file' in emptyObj and emptyObj['file'] in bpy.data.scenes:

                    parentCollection = getParentCollection(context, emptyObj)
                    collections = SEUT_OT_RecreateCollections.getCollections(scn2)

                    collectionType = 'main'
                    if parentCollection == bpy.data.collections['BS1' + tag]:
                        collectionType = 'bs1'
                    elif parentCollection == bpy.data.collections['BS2' + tag]:
                        collectionType = 'bs2'
                    elif parentCollection == bpy.data.collections['BS3' + tag]:
                        collectionType = 'bs3'
                        
                    linkSubpartScene(self, scn2, emptyObj, parentCollection, collectionType)

        # Set parent scenes from subparts
        # Needs to happen in second loop, because first loop needs to first run through all scenes to name them
        for index in range(0, len(bpy.data.scenes)):
            scn = bpy.data.scenes[index]

            for obj in scn.objects:
                if obj.type == 'EMPTY' and 'file' in bpy.data.objects[obj.name] and bpy.data.objects[obj.name]['file'] is not None:
                    subpartScene = bpy.data.objects[obj.name]['file']
                    for i in range(0, len(bpy.data.scenes)):
                        if bpy.data.scenes[i].seut.subtypeId == subpartScene:
                            bpy.data.scenes[i].seut.sceneType = 'subpart'
        
        self.report({'INFO'}, "SEUT: Structure conversion successfully completed.")

        return