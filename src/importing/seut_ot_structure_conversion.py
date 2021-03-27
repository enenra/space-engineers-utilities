import bpy

from bpy.types import Operator

from ..empties.seut_empties          import empty_types
from ..export.seut_export_utils      import get_subpart_reference
from ..seut_collections              import get_collections, rename_collections, create_collections, colors, names
from ..seut_mirroring                import save_rotation
from ..seut_errors                   import seut_report
from ..seut_utils                    import link_subpart_scene, get_parent_collection

class SEUT_OT_StructureConversion(Operator):
    """Ports blend files created with the old plugin to the new structure"""
    bl_idname = "wm.convert_structure"
    bl_label = "Convert to New Structure"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        result = convert_structure(self, context)

        return result
    
    
def convert_structure(self, context):
    """Converts blend files created with the old plugin to the new structure"""

    # For some reason it breaks if you don't run it starting from the scene at index 0
    current_scene = context.window.scene
    context.window.scene = bpy.data.scenes[0]

    # Set scene indexes and SubtypeIds
    for scn in bpy.data.scenes:
        scn.seut.subtypeId = scn.name
        tag = ' (' + scn.seut.subtypeId + ')'

        if 'SEUT' in scn.view_layers:
            for col in bpy.data.collections:
                if col.seut.scene == scn and not col.seut.col_type == 'seut':
                    bpy.data.collections.remove(col)


        else:
            scn.view_layers[0].name = 'SEUT'
            seut_col = bpy.data.collections.new('SEUT' + tag)
            seut_col.seut.scene = scn
            seut_col.seut.col_type = 'seut'
            seut_col.color_tag = colors['seut']
            scn.collection.children.link(seut_col)
        
        assignments = {
            'Collection 1': 'main',
            'Collection 2': 'hkt',
            'Collection 3': 'mountpoints',
            'Collection 4': 'mirroring',
            'Collection 6': 'lod1',
            'Collection 7': 'lod2',
            'Collection 8': 'lod3',
            'Collection 11': 'bs1',
            'Collection 12': 'bs2',
            'Collection 13': 'bs3',
        }
        
        # Convert collections created from layers to corresponding SEUT collections
        for col in scn.collection.children:

            if col.name[:10] != "Collection":
                continue
            
            for key, value in assignments.items():
                if col.name == key or col.name[:len(key) + 1] == key + ".":
                  
                    if not value == 'main' and not value == 'hkt' and not value == 'mountpoints' and not value == 'mirroring':
                        col.seut.type_index = int(value[-1])

                        if value.startswith('bs'):
                            col.seut.col_type = 'bs'
                            value = 'bs'

                        elif value.startswith('lod'):
                            col.seut.col_type = 'lod'
                            if int(value[-1]) == 1:
                                col.seut.lod_distance = 25
                            elif int(value[-1]) == 2:
                                col.seut.lod_distance = 50
                            elif int(value[-1]) == 3:
                                col.seut.lod_distance = 150
                            value = 'lod'

                    else:
                        col.seut.col_type = value
                    
                    if bpy.app.version >= (2, 91, 0):
                        col.color_tag = colors[col.seut.col_type]

                    col.seut.scene = scn

                    if names[value] + tag in bpy.data.collections:
                        bpy.data.collections.remove(bpy.data.collections[names[value] + tag])

                    idx = ""
                    if col.seut.type_index != 0: idx = col.seut.type_index
                    col.name = names[value] + str(idx) + tag

                    break
            
            if not col.name[:4] == 'SEUT':
                scn.collection.children.unlink(col)
                bpy.data.collections['SEUT' + tag].children.link(col)
                
            col.hide_viewport = False

            seut_layer_col = scn.view_layers['SEUT'].layer_collection.children['SEUT' + tag]
            if col.seut.col_type == 'main':
                seut_layer_col.children[col.name].hide_viewport = False
            else:
                seut_layer_col.children[col.name].hide_viewport = True
        
        create_collections(context)
        rename_collections(scn)

        # Convert custom properties of empties from harag's to the default blender method.
        for obj in scn.objects:
            if obj.type == 'EMPTY':

                obj.hide_select = False

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
    
    context.window.scene = current_scene

    # Link up all the subparts for instancing
    for scn in bpy.data.scenes:
        collections = get_collections(scn)

        for key in collections.keys():
            if collections[key] != None:

                if key == 'bs' or key == 'lod' or key == 'bs_lod':
                    for dict_col in collections[key]:
                        for empty in collections[key][dict_col].objects:
                            if empty.type == 'EMPTY' and 'file' in empty and str(empty['file']) in bpy.data.scenes:
                                reference = get_subpart_reference(empty, collections)
                                link_subpart_scene(self, scn, empty, collections[key][dict_col], key)
                                empty['file'] = reference

                elif key == 'main':
                    for empty in collections[key].objects:
                        if empty.type == 'EMPTY' and 'file' in empty and str(empty['file']) in bpy.data.scenes:
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