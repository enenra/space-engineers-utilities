import bpy
import os
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

    # Checks export path and whether SubtypeId exists
    result = check_export(self, context)
    if not result == {'CONTINUE'}:
        return result

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
    path = get_abs_path(scene.seut.export_exportPath) + "\\"

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
    definitions = ET.Element('Definitions')
    definitions.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    definitions.set('xmlns:xsd', 'http://www.w3.org/2001/XMLSchema')

    cube_blocks = ET.SubElement(definitions, 'CubeBlocks')
    def_definition = ET.SubElement(cube_blocks, 'Definition')
    
    def_Id = ET.SubElement(def_definition, 'Id')
    def_TypeId = ET.SubElement(def_Id, 'TypeId')
    def_TypeId.text = 'CubeBlock'
    def_SubtypeId = ET.SubElement(def_Id, 'SubtypeId')
    def_SubtypeId.text = scene.seut.subtypeId

    def_DisplayName = ET.SubElement(def_definition, 'DisplayName')
    def_DisplayName.text = '{LOC:DisplayName_' + scene.seut.subtypeId + '}'
    def_Description = ET.SubElement(def_definition, 'Description')
    def_Description.text = '{LOC:Description_' + scene.seut.subtypeId + '}'
    
    def_Icon = ET.SubElement(def_definition, 'Icon')
    def_Icon.text = 'Textures\GUI\Icons\AstronautBackpack.dds'
    
    def_CubeSize = ET.SubElement(def_definition, 'CubeSize')

    medium_grid_scalar = 1.0 # default to doing nothing unless the 3to5 mode is detected

    if scene.seut.gridScale == 'large':
        def_CubeSize.text = 'Large'
        grid_size = 2.5
        if (abs(scene.seut.export_rescaleFactor - 3) < 0.01): # floating point comparison
            medium_grid_scalar = 0.6 # Large grid block is going to be 3/5 of the expected size
    elif scene.seut.gridScale == 'small':
        def_CubeSize.text = 'Small'
        grid_size = 0.5
        if (abs(scene.seut.export_rescaleFactor - 0.6) < 0.01): # floating point comparison
            medium_grid_scalar = 3.0 # Small grid block is going to be 3 times larger than expected
    
    def_BlockTopology = ET.SubElement(def_definition, 'BlockTopology')
    def_BlockTopology.text = 'TriangleMesh'

    def_Size = ET.SubElement(def_definition, 'Size')
    def_Size.set('x', str(round(scene.seut.bBox_X * medium_grid_scalar)))
    def_Size.set('y', str(round(scene.seut.bBox_Z * medium_grid_scalar)))   # This looks wrong but it's correct: Blender has different forward than SE.
    def_Size.set('z', str(round(scene.seut.bBox_Y * medium_grid_scalar)))

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

        def_Center = ET.SubElement(def_definition, 'Center')
        def_Center.set('x', str(round(medium_grid_scalar * center_loc_x / grid_size)))
        def_Center.set('y', str(round(medium_grid_scalar * center_loc_z / grid_size)))   # This looks wrong but it's correct: Blender has different forward than SE.
        def_Center.set('z', str(round(medium_grid_scalar * center_loc_y / grid_size)))

    def_ModelOffset = ET.SubElement(def_definition, 'ModelOffset')
    def_ModelOffset.set('x', '0')
    def_ModelOffset.set('y', '0')
    def_ModelOffset.set('z', '0')

    # Model
    def_Model = ET.SubElement(def_definition, 'Model')
    def_Model.text = create_relative_path(path, "Models") + scene.seut.subtypeId + '.mwm'

    # Components
    def_Components = ET.SubElement(def_definition, 'Components')
    def_Component = ET.SubElement(def_Components, 'Component')
    def_Component.set('Subtype', 'SteelPlate')
    def_Component.set('Count', '10')

    def_CriticalComponent = ET.SubElement(def_definition, 'CriticalComponent')
    def_CriticalComponent.set('Subtype', 'SteelPlate')
    def_CriticalComponent.set('Index', '0')

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

        def_Mountpoints = ET.SubElement(def_definition, 'MountPoints')

        for area in scene.seut.mountpointAreas:
            if area is not None:

                def_Mountpoint = ET.SubElement(def_Mountpoints, 'MountPoint')
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
                def_Mountpoint.set('a_Side', side_name)
                def_Mountpoint.set('b_StartX', str("{:.2f}".format(round(start_x * medium_grid_scalar, 2))))
                def_Mountpoint.set('c_StartY', str("{:.2f}".format(round(start_y * medium_grid_scalar, 2))))
                def_Mountpoint.set('d_EndX', str("{:.2f}".format(round(end_x * medium_grid_scalar, 2))))
                def_Mountpoint.set('e_EndY', str("{:.2f}".format(round(end_y * medium_grid_scalar, 2))))

                if area.properties_mask:
                    def_Mountpoint.set('f_PropertiesMask', str(area.properties_mask).lower())
                if area.exclusion_mask:
                    def_Mountpoint.set('g_ExclusionMask', str(area.exclusion_mask).lower())
                if area.default:
                    def_Mountpoint.set('h_Default', str(area.default).lower())
                if area.enabled:
                    def_Mountpoint.set('i_Enabled', str(area.enabled).lower())
                if area.pressurized:
                    def_Mountpoint.set('j_PressurizedWhenOpen', str(area.pressurized).lower())

    
    # Build Stages
    if not collections['bs'] is None and len(collections['bs']) > 0:

        counter = 0
        if not collections['bs'] is None:
            for key, value in collections['bs'].items():
                bs_col = value
                if len(bs_col.objects) > 0:
                    counter += 1

        if counter > 0:
            def_BuildProgressModels = ET.SubElement(def_definition, 'BuildProgressModels')

            percentage = 1 / counter

            for bs in range(0, counter):
                def_BS_Model = ET.SubElement(def_BuildProgressModels, 'Model')

                # This makes sure the last build stage is set to upper bound 1.0
                if bs + 1 == counter:
                    def_BS_Model.set('BuildPercentUpperBound', str("{:.2f}".format(1.0)))
                else:
                    def_BS_Model.set('BuildPercentUpperBound', str("{:.2f}".format((bs + 1) * percentage)[:4]))

                def_BS_Model.set('File', create_relative_path(path, "Models") + scene.seut.subtypeId + '_BS' + str(bs + 1) + '.mwm')

    # BlockPairName
    def_BlockPairName = ET.SubElement(def_definition, 'BlockPairName')
    def_BlockPairName.text = scene.seut.subtypeId

    # Mirroring
    if collections['mirroring'] != None:
        scene.seut.mirroringToggle == 'off'

    if scene.seut.mirroring_X != 'None':
        def_MirroringX = ET.SubElement(def_definition, 'MirroringX')
        def_MirroringX.text = scene.seut.mirroring_X
    if scene.seut.mirroring_Z != 'None':                                # This looks wrong but SE works with different Axi than Blender
        def_MirroringY = ET.SubElement(def_definition, 'MirroringY')
        def_MirroringY.text = scene.seut.mirroring_Z
    if scene.seut.mirroring_Y != 'None':
        def_MirroringZ = ET.SubElement(def_definition, 'MirroringZ')
        def_MirroringZ.text = scene.seut.mirroring_Y
    
    # If a MirroringScene is defined, set it in SBC but also set the reference to the base scene in the mirror scene SBC
    if scene.seut.mirroringScene is not None and scene.seut.mirroringScene.name in bpy.data.scenes:
        def_MirroringBlock = ET.SubElement(def_definition, 'MirroringBlock')
        def_MirroringBlock.text = scene.seut.mirroringScene.seut.subtypeId

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

    filename = scene.seut.subtypeId

    exported_xml = open(path + filename + ".sbc", "w")
    exported_xml.write(xml_formatted)

    seut_report(self, context, 'INFO', False, 'I004', path + filename + ".sbc")

    return {'FINISHED'}
