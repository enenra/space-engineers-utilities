import bpy
import os
import re
import glob
import subprocess
import xml.etree.ElementTree as ET
import xml.dom.minidom
import shutil

from os.path        import join
from bpy.types      import Operator

from .havok.seut_havok_options      import HAVOK_OPTION_FILE_CONTENT
from .havok.seut_havok_hkt          import process_hktfbx_to_fbximporterhkt, process_fbximporterhkt_to_final_hkt_for_mwm
from .seut_mwmbuilder               import mwmbuilder
from .seut_export_utils             import ExportSettings, export_to_fbxfile, delete_loose_files, create_relative_path
from .seut_export_utils             import correct_for_export_type, export_xml, export_fbx, export_collection
from ..utils.seut_xml_utils         import *
from ..seut_preferences             import get_addon_version, get_addon
from ..seut_collections             import get_collections, names
from ..seut_errors                  import *
from ..seut_utils                   import prep_context, get_preferences

class SEUT_OT_Export(Operator):
    """Exports all collections in the current scene and compiles them to MWM.\nScene needs to be in Object mode for export to be available"""
    bl_idname = "scene.export"
    bl_label = "Export Current Scene"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.mode == 'OBJECT'
        

    def execute(self, context):
        """Calls the function to export all collections"""

        result = export(self, context)

        return result


def export(self, context):
    """Exports all collections in the current scene and compiles them to MWM"""
    
    scene = context.scene
    collections = get_collections(scene)
    preferences = get_preferences()

    bl_info = get_addon().bl_info
    version = str(bl_info['version']).replace("(","").replace(")","").replace(", ",".")
    if bl_info['dev_version'] > 0:
        version = version + "-" + str(bl_info['dev_tag']) + "." + str(bl_info['dev_version'])

    print("\n============================================================ Exporting Scene '" + scene.name + "' with SEUT " + version + ".")

    current_area = prep_context(context)

    scene.seut.mountpointToggle = 'off'
    scene.seut.mirroringToggle = 'off'
    scene.seut.renderToggle = 'off'

    if not os.path.isdir(scene.seut.mod_path):
        seut_report(self, context, 'ERROR', True, 'E019', "Mod", scene.name)
        return {'CANCELLED'}

    # Checks export path and whether SubtypeId exists
    result = check_export(self, context)
    if not result == {'CONTINUE'}:
        return result
        
    if not os.path.exists(get_abs_path(scene.seut.export_exportPath)):
        os.makedirs(get_abs_path(scene.seut.export_exportPath))

    # Check for availability of FBX Importer
    result = check_toolpath(self, context, preferences.fbx_importer_path, "Custom FBX Importer", "FBXImporter.exe")
    if not result == {'CONTINUE'}:
        return result

    # Check for availability of MWM Builder
    result = check_toolpath(self, context, preferences.mwmb_path, "MWM Builder", "MwmBuilder.exe")
    if not result == {'CONTINUE'}:
        return result

    # Check materials path
    materials_path = get_abs_path(preferences.materials_path)
    if preferences.materials_path == "" or os.path.isdir(materials_path) == False:
        seut_report(self, context, 'ERROR', True, 'E012', "Materials Folder", materials_path)
        return {'CANCELLED'}
    
    # Character animations need at least one keyframe
    if scene.seut.sceneType == 'character_animation' and len(scene.timeline_markers) <= 0:
        scene.timeline_markers.new('F_00', frame=0)
        
    grid_scale = str(scene.seut.gridScale)
    subtype_id = str(scene.seut.subtypeId)
    rescale_factor = int(scene.seut.export_rescaleFactor)
    path = str(scene.seut.export_exportPath)
    
    # Exports large grid and character-type scenes
    if scene.seut.export_largeGrid or scene.seut.sceneType == 'character_animation' or scene.seut.sceneType == 'character':
        scene.seut.gridScale = 'large'
        scene.seut.subtypeId = correct_for_export_type(scene, scene.seut.subtypeId)

        if grid_scale == 'small':
            scene.seut.export_rescaleFactor = 5.0
            if scene.seut.export_medium_grid:
                scene.seut.export_rescaleFactor = 3.0
        else:
            scene.seut.export_rescaleFactor = 1.0

        if scene.seut.export_exportPath.find("\small\\") != -1:
            scene.seut.export_exportPath = scene.seut.export_exportPath.replace("\small\\", "\large\\")
        
        export_all(self, context)

        # Resetting the variables
        scene.seut.subtypeId = subtype_id
        scene.seut.gridScale = grid_scale
        scene.seut.export_rescaleFactor = rescale_factor
        scene.seut.export_exportPath = path
    
    # Exports small grid scenes
    if scene.seut.export_smallGrid:
        scene.seut.gridScale = 'small'
        scene.seut.subtypeId = correct_for_export_type(scene, scene.seut.subtypeId)

        if grid_scale == 'large':
            scene.seut.export_rescaleFactor = 0.2
            if scene.seut.export_medium_grid:
                scene.seut.export_rescaleFactor = 0.6
        else:
            scene.seut.export_rescaleFactor = 1.0

        if scene.seut.export_exportPath.find("\large\\") != -1:
            scene.seut.export_exportPath = scene.seut.export_exportPath.replace("\large\\", "\small\\")
        
        export_all(self, context)

        # Resetting the variables
        scene.seut.subtypeId = subtype_id
        scene.seut.gridScale = grid_scale
        scene.seut.export_rescaleFactor = rescale_factor
        scene.seut.export_exportPath = path
        
    context.area.type = current_area

    return {'FINISHED'}


def export_all(self, context):
    """Exports all collections"""

    scene = context.scene

    export_bs(self, context)
    export_lod(self, context)
    result_main = export_main(self, context)
    export_hkt(self, context)

    if scene.seut.export_sbc and scene.seut.sceneType == 'mainScene':
        export_sbc(self, context)
    
    if result_main == {'FINISHED'}:
        export_mwm(self, context)


def export_main(self, context):
    """Exports the Main collection"""

    scene = context.scene
    collections = get_collections(scene)
    preferences = get_preferences()

    # Checks whether collection exists, is excluded or is empty
    result = check_collection(self, context, scene, collections['main'], False)
    if not result == {'CONTINUE'}:
        return result

    found_armatures = False
    unparented_objects = 0
    for obj in collections['main'].objects:

        if obj is not None and obj.type == 'ARMATURE':
            found_armatures = True
        
        if obj.parent is None and obj.type != 'LIGHT' and obj.type != 'CAMERA':
            unparented_objects += 1
        
        # Check for missing UVMs (this might not be 100% reliable)
        if check_uvms(self, context, obj) != {'CONTINUE'}:
            return {'CANCELLED'}
    
    # Check for armatures being present in collection
    if not found_armatures and (scene.seut.sceneType == 'character' or scene.seut.sceneType == 'character_animation'):
        seut_report(self, context, 'WARNING', True, 'W008', scene.name, scene.seut.sceneType)
    if found_armatures and not (scene.seut.sceneType == 'character' or scene.seut.sceneType == 'character_animation'):
        seut_report(self, context, 'WARNING', True, 'W009', scene.name, scene.seut.sceneType)
    
    # Check for unparented objects
    if unparented_objects > 1:
        seut_report(self, context, 'ERROR', True, 'E031', collections['main'].name)
        return {'CANCELLED'}

    export_collection(self, context, collections['main'])
    
    return {'FINISHED'}


def export_hkt(self, context):
    """Exports collision to HKT"""

    scene = context.scene
    collections = get_collections(scene)
    preferences = get_preferences()
    settings = ExportSettings(scene, None)
    path = get_abs_path(scene.seut.export_exportPath) + "\\"

    # Check for availability of Havok SFM
    result = check_toolpath(self, context, preferences.havok_path, "Havok Standalone Filter Manager", "hctStandAloneFilterManager.exe")
    if not result == {'CONTINUE'}:
        return result

    if not collections['hkt'] is None:
        
        # This exists to determine which HKT is assigned to what FBX.

        # Fill a dictionary with collections as keys
        assignments = {}
        assignments[collections['main']] = None
        for key, value in collections.items():
            if key == 'bs' or key == 'lod' or key == 'bs_lod':
                if not collections[key] is None:
                    for col in collections[key]:
                        assignments[collections[key][col]] = None

        # Assign HKT collections to each key
        for hkt_col in collections['hkt']:

            result = check_collection(self, context, scene, hkt_col, True)
            if not result == {'CONTINUE'}:
                continue

            ref_col = hkt_col.seut.ref_col
            if ref_col.seut.col_type == 'main':
                for key, value in assignments.items():
                    if key.seut.col_type == 'main':
                        assignments[key] = hkt_col
                    elif value is None:
                        assignments[key] = hkt_col

            if ref_col.seut.col_type == 'bs':
                idx = ref_col.seut.type_index
                for key, value in assignments.items():
                    if key.seut.col_type == 'bs' and key.seut.type_index == idx:
                        assignments[key] = hkt_col
                    elif idx == 1 and (key.seut.col_type == 'bs' or key.seut.col_type == 'bs_lod') and value is None:
                        assignments[key] = hkt_col

        # This uses the collision collections as keys for a new dict that contains the assigned "normal" collections as values in a list
        assignments_inverted = {}
        for key, value in assignments.items():
            if not value in assignments_inverted.keys():
                assignments_inverted[value] = []
            if not key in assignments_inverted[value]:
                assignments_inverted[value].append(key)
        
        for hkt_col in collections['hkt']:

            result = check_collection(self, context, scene, hkt_col, True)
            if not result == {'CONTINUE'}:
                continue
            
            cancelled = False
            for obj in hkt_col.objects:

                # Check for unapplied modifiers
                if len(obj.modifiers) > 0:
                    seut_report(self, context, 'ERROR', True, 'E034', obj.name)
                    cancelled = True
                    break
                
                # TODO: Investigate this again, and only apply rigidbody if there isn't one already
                context.view_layer.objects.active = obj
                # bpy.ops.object.transform_apply(location = True, scale = True, rotation = True) # This runs on all objects instead of just the active one for some reason. Breaks when there's instanced subparts.
                bpy.ops.rigidbody.object_add(type='ACTIVE')

            if cancelled:
                return {'CANCELLED'}
            
            if len(hkt_col.objects) > 16:
                seut_report(self, context, 'ERROR', True, 'E022', hkt_col.name, len(hkt_col.objects))
                continue

            # FBX export via Custom FBX Importer
            ref_col = hkt_col.seut.ref_col
            assignments_inverted[hkt_col].remove(ref_col) # This is removed because it's created by default

            tag = ""
            if ref_col.seut.col_type == 'bs':
                tag = "_" + names[ref_col.seut.col_type] + str(ref_col.seut.type_index)

            fbx_hkt_file = join(path, scene.seut.subtypeId + tag + ".hkt.fbx")
            hkt_file = join(path, scene.seut.subtypeId + tag + ".hkt")
            
            export_to_fbxfile(settings, scene, fbx_hkt_file, hkt_col.objects, ishavokfbxfile=True)

            # Then create the HKT file.
            process_hktfbx_to_fbximporterhkt(context, settings, fbx_hkt_file, hkt_file)
            process_fbximporterhkt_to_final_hkt_for_mwm(self, context, path, assignments_inverted[hkt_col], settings, hkt_file, hkt_file)

    return {'FINISHED'}


def export_bs(self, context):
    """Exports Build Stage collections"""

    scene = context.scene
    collections = get_collections(scene)

    valid = {}
    if not collections['bs'] is None:
        for key, value in collections['bs'].items():
            bs_col = value

            valid[key] = False
            result = check_collection(self, context, scene, bs_col, True)
            if result == {'CONTINUE'}:
                valid[key] = True

            if key - 1 in valid and not valid[key - 1] and valid[key]:
                seut_report(self, context, 'ERROR', True, 'E015', 'LOD')
                return {'CANCELLED'}
            
            if valid[key]:
                for obj in bs_col.objects:
                    if check_uvms(self, context, obj) != {'CONTINUE'}:
                        return {'CANCELLED'}
                
                export_collection(self, context, bs_col)
    
    return {'FINISHED'}


def export_lod(self, context):
    """Exports LOD collections"""

    scene = context.scene
    collections = get_collections(scene)

    check_export_lods(self, context, collections['lod'])
    check_export_lods(self, context, collections['bs_lod'])

    return {'FINISHED'}


def check_export_lods(self, context, dictionary):
    scene = context.scene

    valid = {}
    if not dictionary is None:
        for key, value in dictionary.items():
            lod_col = value

            valid[key] = False
            result = check_collection(self, context, scene, lod_col, True)
            if result == {'CONTINUE'}:
                valid[key] = True

            if key - 1 in valid:

                if not valid[key - 1] and valid[key]:
                    seut_report(self, context, 'ERROR', True, 'E015', 'LOD')
                    return {'CANCELLED'}

                if dictionary[key - 1].seut.lod_distance > lod_col.seut.lod_distance:
                    seut_report(self, context, 'ERROR', True, 'E011')
                    return {'CANCELLED'}
            
            if valid[key]:
                for obj in lod_col.objects:
                    if check_uvms(self, context, obj) != {'CONTINUE'}:
                        return {'CANCELLED'}
                
                export_collection(self, context, lod_col)


def export_mwm(self, context):
    """Compiles to MWM from the previously exported temp files"""
    
    scene = context.scene
    collections = get_collections(scene)
    preferences = get_preferences()
    path = get_abs_path(scene.seut.export_exportPath) + "\\"
    materials_path = get_abs_path(preferences.materials_path)
    settings = ExportSettings(scene, None)
        
    mwmfile = join(path, scene.seut.subtypeId + ".mwm")
    
    try:
        mwmbuilder(self, context, path, path, settings, mwmfile, materials_path)
    finally:
        if scene.seut.export_deleteLooseFiles:
            delete_loose_files(self, context, path)

    return {'FINISHED'}


def export_sbc(self, context):
    """Exports to SBC"""

    scene = context.scene
    collections = get_collections(scene)
    preferences = get_preferences()
    path_data = os.path.join(get_abs_path(scene.seut.mod_path), "Data")
    path_models = get_abs_path(scene.seut.export_exportPath)

    # Checks whether collection exists, is excluded or is empty
    result = check_collection(self, context, scene, collections['main'], False)
    if not result == {'CONTINUE'}:
        return result

    bs_valid = {}
    if not collections['bs'] is None:
        for key, value in collections['bs'].items():
            bs_col = value

            bs_valid[key] = False
            result = check_collection(self, context, scene, bs_col, True)
            if result == {'CONTINUE'}:
                bs_valid[key] = True
        
            if key - 1 in bs_valid and not bs_valid[key - 1] and bs_valid[key]:
                seut_report(self, context, 'ERROR', True, 'E015', 'BS')
                return {'CANCELLED'}

    # Create XML tree and add initial parameters.
    file_to_update = None
    root = None
    element = None
    output = get_relevant_sbc(os.path.dirname(path_data), 'CubeBlocks', scene.seut.subtypeId)
    if output is not None:
        file_to_update = output[0]
        root = output[1]
        element = output[2]

    if element is None:
        definitions = ET.Element('Definitions')
        add_attrib(definitions, 'xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        add_attrib(definitions, 'xmlns:xsd', 'http://www.w3.org/2001/XMLSchema')

        cube_blocks = add_subelement(definitions, 'CubeBlocks')
        def_definition = add_subelement(cube_blocks, 'CubeBlock')
        update = False
    
    else:
        definitions = root
        def_definition = element
        update = True
    
    def_Id = add_subelement(def_definition, 'Id')
    add_subelement(def_Id, 'TypeId', 'CubeBlock')
    add_subelement(def_Id, 'SubtypeId', scene.seut.subtypeId)

    add_subelement(def_definition, 'DisplayName', '{LOC:DisplayName_' + scene.seut.subtypeId + '}')
    add_subelement(def_definition, 'Description', '{LOC:Description_' + scene.seut.subtypeId + '}')
    
    add_subelement(def_definition, 'Icon', 'Textures\GUI\Icons\AstronautBackpack.dds')

    medium_grid_scalar = 1.0 # default to doing nothing unless the 3to5 mode is detected

    if scene.seut.gridScale == 'large':
        add_subelement(def_definition, 'CubeSize', 'Large', True)
        grid_size = 2.5
        if (abs(scene.seut.export_rescaleFactor - 3) < 0.01): # floating point comparison
            medium_grid_scalar = 0.6 # Large grid block is going to be 3/5 of the expected size
    elif scene.seut.gridScale == 'small':
        add_subelement(def_definition, 'CubeSize', 'Small', True)
        grid_size = 0.5
        if (abs(scene.seut.export_rescaleFactor - 0.6) < 0.01): # floating point comparison
            medium_grid_scalar = 3.0 # Small grid block is going to be 3 times larger than expected
    
    add_subelement(def_definition, 'BlockTopology', 'TriangleMesh')

    def_Size = add_subelement(def_definition, 'Size')
    add_attrib(def_Size, 'x', round(scene.seut.bBox_X * medium_grid_scalar), True)
    add_attrib(def_Size, 'y', round(scene.seut.bBox_Z * medium_grid_scalar), True)   # This looks wrong but it's correct: Blender has different forward than SE.
    add_attrib(def_Size, 'z', round(scene.seut.bBox_Y * medium_grid_scalar), True)

    center_empty = None
    for obj in collections['main'].objects:
        if obj is not None and obj.type == 'EMPTY' and obj.name.startswith('Center'):
            center_empty = obj
            break

    if center_empty is not None:
        center_loc_x = center_empty.location.x
        center_loc_y = center_empty.location.y
        center_loc_z = center_empty.location.z

        parent_obj = center_empty.parent

        while parent_obj is not None:
            center_loc_x += parent_obj.location.x
            center_loc_y += parent_obj.location.y
            center_loc_z += parent_obj.location.z
            parent_obj = parent_obj.parent

        def_Center = add_subelement(def_definition, 'Center')
        add_attrib(def_Center, 'x', round(medium_grid_scalar * center_loc_x / grid_size), True)
        add_attrib(def_Center, 'y', round(medium_grid_scalar * center_loc_z / grid_size), True)   # This looks wrong but it's correct: Blender has different forward than SE.
        add_attrib(def_Center, 'z', round(medium_grid_scalar * center_loc_y / grid_size), True)

    def_ModelOffset = add_subelement(def_definition, 'ModelOffset')
    add_attrib(def_ModelOffset, 'x', 0)
    add_attrib(def_ModelOffset, 'y', 0)
    add_attrib(def_ModelOffset, 'z', 0)

    # Model
    add_subelement(def_definition, 'Model', os.path.join(create_relative_path(path_models, "Models"), scene.seut.subtypeId + '.mwm'), True)

    # Components
    def_Components = add_subelement(def_definition, 'Components')
    def_Component = add_subelement(def_Components, 'Component')
    add_attrib(def_Component, 'Subtype', 'SteelPlate')
    add_attrib(def_Component, 'Count', 10)

    def_CriticalComponent = add_subelement(def_definition, 'CriticalComponent')
    add_attrib(def_CriticalComponent, 'Subtype', 'SteelPlate')
    add_attrib(def_CriticalComponent, 'Index', 0)

    # Mountpoints
    if collections['mountpoints'] != None:
        scene.seut.mountpointToggle == 'off'
    
    if len(scene.seut.mountpointAreas) > 0:

        # gridScale here is modified when exporting both types, use rescaleFactor to determine original gridScale used to define mountpoints
        if (scene.seut.gridScale == 'small' and scene.seut.export_rescaleFactor > 0.99) or (scene.seut.gridScale == "large" and scene.seut.export_rescaleFactor > 1.01):
            scale = 0.5
        else:
            scale = 2.5

        bbox_x = scene.seut.bBox_X * scale
        bbox_y = scene.seut.bBox_Y * scale
        bbox_z = scene.seut.bBox_Z * scale

        # Wipe existing ones.
        for elem in def_definition:
            if elem.tag == 'MountPoints':
                def_definition.remove(elem)

        def_Mountpoints = add_subelement(def_definition, 'MountPoints')

        for area in scene.seut.mountpointAreas:
            if area is not None:

                def_Mountpoint = add_subelement(def_Mountpoints, 'MountPoint')
                side_name = area.side.capitalize()

                if area.side == 'front' or area.side == 'back':
                    if area.x + (area.xDim / 2) - (bbox_x / 2) > 0:
                        start_x = 0.0
                    else:
                        start_x = abs(area.x + (area.xDim / 2) - (bbox_x / 2)) / scale

                    if area.y + (area.yDim / 2) - (bbox_z / 2) > 0:
                        start_y = 0.0
                    else:
                        start_y = abs(area.y + (area.yDim / 2) - (bbox_z / 2)) / scale

                    end_x = abs(area.x - (area.xDim / 2) - (bbox_x / 2)) / scale
                    end_y = abs(area.y - (area.yDim / 2) - (bbox_z / 2)) / scale

                    if end_x > scene.seut.bBox_X:
                        end_x = scene.seut.bBox_X
                    if end_y > scene.seut.bBox_Z:
                        end_y = scene.seut.bBox_Z

                elif area.side == 'left' or area.side == 'right':
                    if area.x + (area.xDim / 2) - (bbox_y / 2) > 0:
                        start_x = 0.0
                    else:
                        start_x = abs(area.x + (area.xDim / 2) - (bbox_y / 2)) / scale

                    if area.y + (area.yDim / 2) - (bbox_z / 2) > 0:
                        start_y = 0.0
                    else:
                        start_y = abs(area.y + (area.yDim / 2) - (bbox_z / 2)) / scale
                        
                    end_x = abs(area.x - (area.xDim / 2) - (bbox_y / 2)) / scale
                    end_y = abs(area.y - (area.yDim / 2) - (bbox_z / 2)) / scale

                    if end_x > scene.seut.bBox_Y:
                        end_x = scene.seut.bBox_Y
                    if end_y > scene.seut.bBox_Z:
                        end_y = scene.seut.bBox_Z

                elif area.side == 'top' or area.side == 'bottom':
                    if area.x + (area.xDim / 2) - (bbox_x / 2) > 0:
                        start_x = 0.0
                    else:
                        start_x = abs(area.x + (area.xDim / 2) - (bbox_x / 2)) / scale

                    if area.y + (area.yDim / 2) - (bbox_y / 2) > 0:
                        start_y = 0.0
                    else:
                        start_y = abs(area.y + (area.yDim / 2) - (bbox_y / 2)) / scale

                    end_x = abs(area.x - (area.xDim / 2) - (bbox_x / 2)) / scale
                    end_y = abs(area.y - (area.yDim / 2) - (bbox_y / 2)) / scale

                    if end_x > scene.seut.bBox_X:
                        end_x = scene.seut.bBox_X
                    if end_y > scene.seut.bBox_Y:
                        end_y = scene.seut.bBox_Y

                # Need to do this to prevent ET from auto-rearranging keys.
                add_attrib(def_Mountpoint, 'a_Side', side_name)
                add_attrib(def_Mountpoint, 'b_StartX', "{:.2f}".format(round(start_x * medium_grid_scalar, 2)), True)
                add_attrib(def_Mountpoint, 'c_StartY', "{:.2f}".format(round(start_y * medium_grid_scalar, 2)), True)
                add_attrib(def_Mountpoint, 'd_EndX', "{:.2f}".format(round(end_x * medium_grid_scalar, 2)), True)
                add_attrib(def_Mountpoint, 'e_EndY', "{:.2f}".format(round(end_y * medium_grid_scalar, 2)), True)

                if area.properties_mask:
                    add_attrib(def_Mountpoint, 'f_PropertiesMask', str(area.properties_mask).lower(), True)
                if area.exclusion_mask:
                    add_attrib(def_Mountpoint, 'g_ExclusionMask', str(area.exclusion_mask).lower(), True)
                if not area.enabled:
                    add_attrib(def_Mountpoint, 'h_Enabled', str(area.enabled).lower(), True)
                if area.default:
                    add_attrib(def_Mountpoint, 'i_Default', str(area.default).lower(), True)
                if area.pressurized:
                    add_attrib(def_Mountpoint, 'j_PressurizedWhenOpen', str(area.pressurized).lower(), True)

    
    # Build Stages
    if not collections['bs'] is None and len(collections['bs']) > 0:

        counter = 0
        if not collections['bs'] is None:
            for key, value in collections['bs'].items():
                bs_col = value
                if len(bs_col.objects) > 0:
                    counter += 1

        if counter > 0:
            def_BuildProgressModels = add_subelement(def_definition, 'BuildProgressModels')

            percentage = 1 / counter

            for bs in range(0, counter):
                def_BS_Model = ET.SubElement(def_BuildProgressModels, 'Model')

                # This makes sure the last build stage is set to upper bound 1.0
                if bs + 1 == counter:
                    add_attrib(def_BS_Model, 'BuildPercentUpperBound', "{:.2f}".format(1.0), True)
                else:
                    add_attrib(def_BS_Model, 'BuildPercentUpperBound', "{:.2f}".format((bs + 1) * percentage)[:4], True)

                add_attrib(def_BS_Model, 'File', os.path.join(create_relative_path(path_models, "Models"), scene.seut.subtypeId + '_BS' + str(bs + 1) + '.mwm'), True)

    # BlockPairName
    add_subelement(def_definition, 'BlockPairName', scene.seut.subtypeId)

    # Mirroring
    if collections['mirroring'] != None:
        scene.seut.mirroringToggle == 'off'

    if scene.seut.mirroring_X != 'None':
        add_subelement(def_definition, 'MirroringX', scene.seut.mirroring_X)
    if scene.seut.mirroring_Z != 'None':                                # This looks wrong but SE works with different Axi than Blender
        add_subelement(def_definition, 'MirroringY', scene.seut.mirroring_Z)
    if scene.seut.mirroring_Y != 'None':
        add_subelement(def_definition, 'MirroringZ', scene.seut.mirroring_Y)
    
    # If a MirroringScene is defined, set it in SBC but also set the reference to the base scene in the mirror scene SBC
    if scene.seut.mirroringScene is not None and scene.seut.mirroringScene.name in bpy.data.scenes:
        add_subelement(def_definition, 'MirroringBlock', scene.seut.mirroringScene.seut.subtypeId)

    # Write to file, place in export folder
    temp_string = ET.tostring(definitions, 'utf-8')
    try:
        temp_string.decode('ascii')
    except UnicodeDecodeError:
        seut_report(self, context, 'ERROR', True, 'E033')
    xml_string = xml.dom.minidom.parseString(temp_string)
    xml_formatted = xml_string.toprettyxml()

    # Fixing the entries
    xml_formatted = xml_formatted.replace("a_Side", "Side")
    xml_formatted = xml_formatted.replace("b_StartX", "StartX")
    xml_formatted = xml_formatted.replace("c_StartY", "StartY")
    xml_formatted = xml_formatted.replace("d_EndX", "EndX")
    xml_formatted = xml_formatted.replace("e_EndY", "EndY")
    xml_formatted = xml_formatted.replace("f_PropertiesMask", "PropertiesMask")
    xml_formatted = xml_formatted.replace("g_ExclusionMask", "ExclusionMask")
    xml_formatted = xml_formatted.replace("h_Enabled", "Enabled")
    xml_formatted = xml_formatted.replace("i_Default", "Default")
    xml_formatted = xml_formatted.replace("j_PressurizedWhenOpen", "PressurizedWhenOpen")
    
    xml_formatted = re.sub(r'\n\s*\n', '\n', xml_formatted)

    filename = scene.seut.subtypeId

    if update:
        target_file = file_to_update
    else:
        target_file = os.path.join(path_data, "CubeBlocks", filename + ".sbc")
        if not os.path.exists(os.path.join(path_data, "CubeBlocks")):
            os.makedirs(os.path.join(path_data, "CubeBlocks"))

    exported_xml = open(target_file, "w")
    exported_xml.write(xml_formatted)

    seut_report(self, context, 'INFO', False, 'I004', target_file)

    return {'FINISHED'}
