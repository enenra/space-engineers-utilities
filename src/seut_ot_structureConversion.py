import bpy

from bpy.types import Operator

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

        scene = context.scene

        # Set scene indexes and SubtypeIds
        for index in range(0, len(bpy.data.scenes)):
            scn = bpy.data.scenes[index]

            if scn.seut.index == -1:
                scn.seut.index = index
                scn.seut.subtypeId = scn.name
                # For inactive scenes, the update doesn't trigger apparently, so I have to add the index to the scene names manually.
                if index > 0:
                    scn.name = scn.name + ' (' + str(scn.seut.index) + ')'
            
            # Create main SEUT collection for each scene
            seut = bpy.data.collections.new('SEUT' + ' (' + str(scn.seut.index) + ')')
            scn.collection.children.link(seut)

            
            # convert collections created from layers to corresponding SEUT collections
            for collection in scn.collection.children:

                if collection.name == 'Collection 1' or collection.name[:13] == 'Collection 1.':
                    collection.name = 'Main' + ' (' + str(scn.seut.index) + ')'
                    
                elif collection.name == 'Collection 2' or collection.name[:13] == 'Collection 2.':
                    collection.name = 'Collision' + ' (' + str(scn.seut.index) + ')'
                    
                elif collection.name == 'Collection 3' or collection.name[:13] == 'Collection 3.':
                    collection.name = 'MountPoints' + ' (' + str(scn.seut.index) + ')'
                    
                elif collection.name == 'Collection 4' or collection.name[:13] == 'Collection 4.':
                    collection.name = 'Mirroring' + ' (' + str(scn.seut.index) + ')'
                    
                elif collection.name == 'Collection 6' or collection.name[:13] == 'Collection 6.':
                    collection.name = 'LOD1' + ' (' + str(scn.seut.index) + ')'
                    
                elif collection.name == 'Collection 7' or collection.name[:13] == 'Collection 7.':
                    collection.name = 'LOD2' + ' (' + str(scn.seut.index) + ')'
                    
                elif collection.name == 'Collection 8' or collection.name[:13] == 'Collection 8.':
                    collection.name = 'LOD3' + ' (' + str(scn.seut.index) + ')'
                    
                elif collection.name == 'Collection 11' or collection.name[:14] == 'Collection 11.':
                    collection.name = 'BS1' + ' (' + str(scn.seut.index) + ')'
                    
                elif collection.name == 'Collection 12' or collection.name[:14] == 'Collection 12.':
                    collection.name = 'BS2' + ' (' + str(scn.seut.index) + ')'
                    
                elif collection.name == 'Collection 13' or collection.name[:14] == 'Collection 13.':
                    collection.name = 'BS3' + ' (' + str(scn.seut.index) + ')'
                
                if not collection.name[:4] == 'SEUT':
                    scn.collection.children.unlink(collection)
                    bpy.data.collections['SEUT' + ' (' + str(scn.seut.index) + ')'].children.link(collection)
                
        # convert LOD distances? and other variables

        # how to handle custom materials?

        return