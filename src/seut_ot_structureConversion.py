import bpy

from bpy.types import Operator

from .seut_utils    import linkSubpartScene

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
        bpy.context.window.scene = bpy.data.scenes[0]

        # Set scene indexes and SubtypeIds
        for scn in bpy.data.scenes:
            scn.seut.subtypeId = scn.name
            tag = ' (' + scn.seut.subtypeId + ')'
            
            # Create main SEUT collection for each scene
            seutExists = False
            for collection in scn.collection.children:
                if collection.name[:4] == 'SEUT':
                    seutExists = True

            if not seutExists:
                seut = bpy.data.collections.new('SEUT' + tag)
                scn.collection.children.link(seut)
            
            # convert collections created from layers to corresponding SEUT collections
            for collection in scn.collection.children:

                if collection.name == 'Collection 1' or collection.name[:13] == 'Collection 1.':
                    collection.name = 'Main' + tag
                    
                elif collection.name == 'Collection 2' or collection.name[:13] == 'Collection 2.':
                    collection.name = 'Collision' + tag
                    
                elif collection.name == 'Collection 3' or collection.name[:13] == 'Collection 3.':
                    collection.name = 'MountPoints' + tag
                    
                elif collection.name == 'Collection 4' or collection.name[:13] == 'Collection 4.':
                    collection.name = 'Mirroring' + tag
                    
                elif collection.name == 'Collection 6' or collection.name[:13] == 'Collection 6.':
                    collection.name = 'LOD1' + tag
                    
                elif collection.name == 'Collection 7' or collection.name[:13] == 'Collection 7.':
                    collection.name = 'LOD2' + tag
                    
                elif collection.name == 'Collection 8' or collection.name[:13] == 'Collection 8.':
                    collection.name = 'LOD3' + tag
                    
                elif collection.name == 'Collection 11' or collection.name[:14] == 'Collection 11.':
                    collection.name = 'BS1' + tag
                    
                elif collection.name == 'Collection 12' or collection.name[:14] == 'Collection 12.':
                    collection.name = 'BS2' + tag
                    
                elif collection.name == 'Collection 13' or collection.name[:14] == 'Collection 13.':
                    collection.name = 'BS3' + tag
                
                if not collection.name[:4] == 'SEUT':
                    scn.collection.children.unlink(collection)
                    bpy.data.collections['SEUT' + tag].children.link(collection)
                
            # Convert custom properties of empties from harag's to the default blender method.
            for obj in scn.objects:
                if obj.type == 'EMPTY':
                    obj.empty_display_type = "CUBE"

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
        
        bpy.context.window.scene = currentScene

        for scn2 in bpy.data.scenes:
            for emptyObj in scn2.objects:
                if emptyObj.type == 'EMPTY' and 'file' in emptyObj and emptyObj['file'] in bpy.data.scenes:
                    linkSubpartScene(self, scn2, emptyObj, emptyObj.seut.linkedScene)

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