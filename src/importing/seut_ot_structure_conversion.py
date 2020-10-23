import bpy

from bpy.types import Operator

from ..empties.seut_empties          import empty_types
from ..export.seut_export_utils      import get_subpart_reference
from ..seut_collections              import get_collections
from ..seut_mirroring                import save_rotation
from ..seut_errors                   import seut_report
from ..seut_utils                    import link_subpart_scene, get_parent_collection


class SEUT_OT_StructureConversion(Operator):
    """Ports blend files created with the old plugin to the new structure"""
    bl_idname = "wm.convert_structure"
    bl_label = "Convert to new structure"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        result = convert_structure(self, context)

        return result
    
    
def convert_structure(self, context):
    """Converts blend files created with the old plugin to the new structure"""

    # For some reason it breaks if you don't run it starting from the scene at index 0
    current_scene = bpy.context.window.scene
    context.window.scene = bpy.data.scenes[0]

    # Set scene indexes and SubtypeIds
    for scn in bpy.data.scenes:
        scn.seut.subtypeId = scn.name
        tag = ' (' + scn.seut.subtypeId + ')'
        
        # Create main SEUT collection for each scene
        seut_exists = False
        for collection in scn.collection.children:
            if collection.name == 'SEUT' + tag:
                seut_exists = True

        if not seut_exists:
            scn.view_layers[0].name = 'SEUT'
            seut = bpy.data.collections.new('SEUT' + tag)
            scn.collection.children.link(seut)
        
        assignments = {
            'Collection 1': 'Main',
            'Collection 2': 'Collision',
            'Collection 3': 'Mountpoints',
            'Collection 4': 'Mirroring',
            'Collection 6': 'LOD1',
            'Collection 7': 'LOD2',
            'Collection 8': 'LOD3',
            'Collection 11': 'BS1',
            'Collection 12': 'BS2',
            'Collection 13': 'BS3',
        }
        
        # Convert collections created from layers to corresponding SEUT collections
        for col in scn.collection.children:

            if col.name[:10] != "Collection":
                continue

            for key in assignments.keys():
                if col.name == key or col.name[:len(key) + 1] == key + ".":
                    if assignments[key] + tag in bpy.data.collections:
                        bpy.data.collections.remove(bpy.data.collections[assignments[key] + tag])
                    col.name = assignments[key] + tag
                    break
            
            if not col.name[:4] == 'SEUT':
                scn.collection.children.unlink(col)
                bpy.data.collections['SEUT' + tag].children.link(col)
            
            col.hide_viewport = False
            
        # Convert custom properties of empties from harag's to the default blender method.
        for obj in scn.objects:
            if obj.type == 'EMPTY':

                obj.empty_display_type = 'CUBE'
                for key in empty_types.keys():
                    if obj.name[:len(key)] == key:
                        obj.empty_display_type = empty_types[key]
                        break

                if 'space_engineers' in obj and obj['space_engineers'] is not None:
                    harag_prop = obj['space_engineers']

                    target_object_name = None
                    if harag_prop.get('highlight_objects') is not None:
                        custom_prop_name = 'highlight'
                        target_object_name = harag_prop.get('highlight_objects')

                        if target_object_name in bpy.data.objects:
                            obj.seut.linkedObject = bpy.data.objects[target_object_name]

                    elif harag_prop.get('file') is not None:
                        custom_prop_name = 'file'
                        custom_prop_value = harag_prop.get('file')

                        if custom_prop_value.find('_Large') != -1:
                            target_object_name = custom_prop_value[:custom_prop_value.rfind('_Large')]
                        if custom_prop_value.find('_Small') != -1:
                            target_object_name = custom_prop_value[:custom_prop_value.rfind('_Small')]
                        else:
                            target_object_name = custom_prop_value

                    if target_object_name is not None:
                        bpy.data.objects[obj.name][custom_prop_name] = target_object_name
                        del obj['space_engineers']
                        
                        if target_object_name in bpy.data.scenes:
                            obj.seut.linkedScene = bpy.data.scenes[target_object_name]
    
        # Convert Mirroring information
        if 'Mirroring' + tag in bpy.data.collections:
            for mirror_empty in bpy.data.collections['Mirroring' + tag].objects:
                if mirror_empty.type == 'EMPTY':
                    if mirror_empty.name == 'MirrorFrontBack':
                        mirror_empty.name = 'Mirroring X'
                        save_rotation(self, context, mirror_empty)
                    elif mirror_empty.name == 'MirrorLeftRight':
                        mirror_empty.name = 'Mirroring Y'
                        save_rotation(self, context, mirror_empty)
                    elif mirror_empty.name == 'MirrorTopBottom':
                        mirror_empty.name = 'Mirroring Z'
                        save_rotation(self, context, mirror_empty)
                
            scn.seut.mirroringToggle = 'off'
        
        # Clean up mountpoints - cannot convert them
        if 'Mountpoints' + tag in bpy.data.collections:
            for mp in bpy.data.collections['Mountpoints' + tag].objects:
                for child in mp.children:
                    bpy.data.objects.remove(child)
                mp.select_set(state=False, view_layer=context.window.view_layer)
                bpy.data.objects.remove(mp)
            bpy.data.collections.remove(bpy.data.collections['Mountpoints' + tag])
    
    bpy.context.window.scene = current_scene

    # Link up all the subparts for instancing
    for scn in bpy.data.scenes:
        collections = get_collections(scn)

        for key in collections.keys():
            if collections[key] != None:
                for empty in collections[key].objects:
                    if empty.type == 'EMPTY' and 'file' in empty and empty['file'] in bpy.data.scenes:
                        reference = get_subpart_reference(empty, collections)                        
                        link_subpart_scene(self, scn, empty, collections[key], key)
                        empty['file'] = reference

    # Set parent scenes from subparts
    # Needs to happen in second loop, because first loop needs to first run through all scenes to name them
    for index in range(0, len(bpy.data.scenes)):
        scn = bpy.data.scenes[index]

        for obj in scn.objects:
            if obj.type == 'EMPTY' and 'file' in bpy.data.objects[obj.name] and bpy.data.objects[obj.name]['file'] is not None:
                subpart_scene_name = bpy.data.objects[obj.name]['file']
                for i in range(0, len(bpy.data.scenes)):
                    if bpy.data.scenes[i].seut.subtypeId == subpart_scene_name:
                        bpy.data.scenes[i].seut.sceneType = 'subpart'
    
    seut_report(self, context, 'INFO', True, 'I012')

    return {'FINISHED'}