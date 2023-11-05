import bpy
import os
import math
import xml.etree.ElementTree as ET
import xml.dom.minidom
import shutil

from os.path        import join
from bpy.types      import Operator

from .havok.seut_havok_hkt          import convert_fbx_to_fbxi_hkt, convert_fbxi_hkt_to_hkt
from .seut_mwmbuilder               import mwmbuilder
from .seut_export_utils             import ExportSettings, export_to_fbxfile, create_relative_path
from .seut_export_utils             import correct_for_export_type, export_collection, get_col_filename, convert_position_to_cell
from ..utils.seut_xml_utils         import *
from ..seut_collections             import get_collections, get_rev_ref_cols, get_cols_by_type, get_first_free_index
from ..seut_errors                  import *
from ..seut_utils                   import prep_context, get_preferences, create_relative_path, get_addon
from ..utils.seut_tool_utils        import get_tool_dir


orig_grid_scale = ""


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
    preferences = get_preferences()

    active_col = context.view_layer.active_layer_collection

    bl_info = get_addon().bl_info
    version = str(bl_info['version']).replace("(","").replace(")","").replace(", ",".")
    if bl_info['dev_version'] > 0:
        version = f"{version}-{str(bl_info['dev_tag'])}.{str(bl_info['dev_version'])}"

    print("\n============================================================ Exporting Scene '" + scene.name + "' with SEUT " + version + ".")

    current_area = prep_context(context)

    scene.seut.mountpointToggle = 'off'
    scene.seut.mirroringToggle = 'off'
    scene.seut.renderToggle = 'off'

    subparts = scene.seut.linkSubpartInstances
    scene.seut.linkSubpartInstances = False

    if not os.path.isdir(get_abs_path(scene.seut.mod_path) + '\\'):
        seut_report(self, context, 'ERROR', True, 'E019', "Mod", scene.name)
        scene.seut.linkSubpartInstances = subparts
        return {'CANCELLED'}

    # Checks export path and whether SubtypeId exists
    result = check_export(self, context)
    if not result == {'CONTINUE'}:
        scene.seut.linkSubpartInstances = subparts
        return result
        
    if not os.path.exists(get_abs_path(scene.seut.export_exportPath)):
        os.makedirs(get_abs_path(scene.seut.export_exportPath))

    # Check for availability of FBX Importer
    result = check_toolpath(self, context, os.path.join(get_tool_dir(), 'FBXImporter.exe'), "Custom FBX Importer", "FBXImporter.exe")
    if not result == {'CONTINUE'}:
        scene.seut.linkSubpartInstances = subparts
        return result

    # Check for availability of MWM Builder
    result = check_toolpath(self, context, preferences.mwmb_path, "MWM Builder", "MwmBuilder.exe")
    if not result == {'CONTINUE'}:
        scene.seut.linkSubpartInstances = subparts
        return result

    # Check materials path
    materials_path = os.path.join(get_abs_path(preferences.asset_path), 'Materials')
    if preferences.asset_path == "":
        seut_report(self, context, 'ERROR', True, 'E012', "Asset Directory", get_abs_path(preferences.asset_path))
        scene.seut.linkSubpartInstances = subparts
        return {'CANCELLED'}
    elif not os.path.isdir(materials_path):
        os.makedirs(materials_path, exist_ok=True)
    
    # Character animations need at least one keyframe
    if scene.seut.sceneType == 'character_animation' and len(scene.timeline_markers) <= 0:
        scene.timeline_markers.new('F_00', frame=0)
        
    grid_scale = str(scene.seut.gridScale)
    global orig_grid_scale
    orig_grid_scale = grid_scale
    subtype_id = str(scene.seut.subtypeId)
    rescale_factor = int(scene.seut.export_rescaleFactor)
    path = str(scene.seut.export_exportPath)
    
    # Exports large grid and character-type scenes
    if scene.seut.export_largeGrid or scene.seut.sceneType in ['character','character_animation']:
        scene.seut.gridScale = 'large'
        scene.seut.subtypeId = correct_for_export_type(scene, scene.seut.subtypeId)

        if grid_scale == 'small':
            scene.seut.export_rescaleFactor = 5.0
            if scene.seut.export_medium_grid:
                scene.seut.export_rescaleFactor = 3.0
        else:
            scene.seut.export_rescaleFactor = 1.0

        if scene.seut.export_exportPath.find("\small\\") != -1 or scene.seut.export_exportPath.endswith("\small"):
            scene.seut.export_exportPath = scene.seut.export_exportPath.replace("\small\\", "\large\\")
            scene.seut.export_exportPath = scene.seut.export_exportPath.replace("\small", "\large")
        
        result = export_all(self, context)

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

        if scene.seut.export_exportPath.find("\large\\") != -1 or scene.seut.export_exportPath.endswith("\large"):
            scene.seut.export_exportPath = scene.seut.export_exportPath.replace("\large\\", "\small\\")
            scene.seut.export_exportPath = scene.seut.export_exportPath.replace("\large", "\small")
        
        result = export_all(self, context)

        # Resetting the variables
        scene.seut.subtypeId = subtype_id
        scene.seut.gridScale = grid_scale
        scene.seut.export_rescaleFactor = rescale_factor
        scene.seut.export_exportPath = path
        
    scene.seut.linkSubpartInstances = subparts
    
    context.area.type = current_area
    context.view_layer.active_layer_collection = active_col

    return result


def export_all(self, context):
    """Exports all collections"""

    scene = context.scene

    results = []

    results.append(export_bs(self, context))
    results.append(export_lod(self, context))
    results.append(export_main(self, context))
    results.append(export_hkt(self, context))

    if scene.seut.export_sbc_type in ['update', 'new'] and scene.seut.sceneType == 'mainScene':
        results.append(export_sbc(self, context))
    
    if {'CANCELLED'} not in results:
        export_mwm(self, context)
        return {'FINISHED'}
    else:
        return {'CANCELLED'}


def export_main(self, context):
    """Exports the Main collection"""

    scene = context.scene
    collections = get_collections(scene)

    # Checks whether collection exists, is excluded or is empty
    result = check_collection(self, context, scene, collections['main'][0], False)
    if result != {'CONTINUE'}:
        return result

    # This prevents issues ingame. Might have to be revisited for animations.
    scene.frame_current = 0

    found_armatures = False
    unparented_objects = 0
    for obj in collections['main'][0].objects:

        if scene.seut.sceneType == 'chraracter' and check_weights(context, obj) is False:
            return {'CANCELLED'}

        if obj is not None and obj.type == 'ARMATURE':
            found_armatures = True

        if obj.parent is None and obj.type != 'LIGHT' and obj.type != 'CAMERA':
            unparented_objects += 1

        # Check for missing UVMs (this might not be 100% reliable)
        if check_uvms(self, context, obj) != {'CONTINUE'}:
            return {'CANCELLED'}
        
        if obj.type == 'EMPTY' and 'file' in obj and not obj.seut.linked:
            if orig_grid_scale == 'large' and scene.seut.export_smallGrid or orig_grid_scale == 'small' and scene.seut.export_largeGrid:
                seut_report(self, context, 'WARNING', True, 'W020', scene.name, obj.name)

    # Check for armatures being present in collection
    if not found_armatures and scene.seut.sceneType in ['character','character_animation',]:
        seut_report(self, context, 'WARNING', True, 'W008', scene.name, scene.seut.sceneType)
    if found_armatures and scene.seut.sceneType not in ['character','character_animation',]:
        seut_report(self, context, 'WARNING', True, 'W009', scene.name, scene.seut.sceneType)

    # Check for unparented objects
    if unparented_objects > 1:
        seut_report(self, context, 'ERROR', True, 'E031', collections['main'][0].name)
        return {'CANCELLED'}

    results = export_collection(self, context, collections['main'][0])            
    if {'CANCELLED'} in results:
        return {'CANCELLED'}

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

    if 'hkt' in collections and not collections['hkt'] is None and collections['hkt'] != []:
        for col in collections['hkt']:

            # Use external file
            if col.seut.hkt_file != "":
                shutil.copyfile(get_abs_path(col.seut.hkt_file), join(path, f"{get_col_filename(col)}.hkt"))

            else:
                result = check_collection(self, context, scene, col, True)
                if not result == {'CONTINUE'}:
                    continue

                cancelled = False
                for obj in col.objects:

                    # Check for unapplied modifiers
                    if len(obj.modifiers) > 0:
                        seut_report(self, context, 'ERROR', True, 'E034', obj.name)
                        cancelled = True
                        break

                    if obj.rigid_body.collision_shape == 'COMPOUND':
                        seut_report(self, context, 'ERROR', True, 'E054', obj.name, col.name)
                        cancelled = True
                        break

                    # TODO: Investigate this again, and only apply rigidbody if there isn't one already
                    context.view_layer.objects.active = obj
                    # bpy.ops.object.transform_apply(location = True, scale = True, rotation = True) # This runs on all objects instead of just the active one for some reason. Breaks when there's instanced subparts.
                    bpy.ops.rigidbody.object_add(type='ACTIVE')

                if cancelled:
                    return {'CANCELLED'}

                if len(col.objects) > 10:
                    seut_report(self, context, 'ERROR', True, 'E022', col.name, len(col.objects))
                    continue

                fbx_hkt_file = join(path, f"{get_col_filename(col)}.hkt.fbx")
                hkt_file = join(path, f"{get_col_filename(col)}.hkt")

                # Export as FBX
                export_to_fbxfile(settings, scene, fbx_hkt_file, col.objects, ishavokfbxfile=True)

                # Then create the HKT file.
                convert_fbx_to_fbxi_hkt(context, settings, fbx_hkt_file, hkt_file)
                convert_fbxi_hkt_to_hkt(self, context, settings, hkt_file, hkt_file)

    return {'FINISHED'}


def export_bs(self, context):
    """Exports Build Stage collections"""

    scene = context.scene
    bs_cols = get_cols_by_type(scene, 'bs')
    result = check_export_col_dict(self, context, bs_cols)
    
    return result


def export_lod(self, context):
    """Exports LOD collections"""

    scene = context.scene
    collections = get_collections(scene)

    # Normal LODs
    lod_cols = get_cols_by_type(scene, 'lod', collections['main'][0])
    result_normal = check_export_col_dict(self, context, lod_cols)

    # BS LODs
    if 'bs' in collections:
        if collections['bs'] is not None:
            for ref_col in collections['bs']:
                lod_cols = get_cols_by_type(scene, 'lod', ref_col)
                result_bslod = check_export_col_dict(self, context, lod_cols)
                if result_bslod == {'CANCELLED'}:
                    return {'CANCELLED'}

    if result_normal == {'CANCELLED'}:
        return {'CANCELLED'}

    return {'FINISHED'}


def check_export_col_dict(self, context, cols: dict):
    scene = context.scene
    first_free_idx = get_first_free_index(cols)

    # This ensures there's no index gaps
    if first_free_idx <= len(cols):
        col = next(iter(cols.values()))
        col_type = col.seut.col_type
        if col_type == 'lod' and col.seut.ref_col is not None:
            ref_col_type_index = col.seut.ref_col.seut.type_index
            seut_report(self, context, 'ERROR', True, 'E006', f"BS{ref_col_type_index}_LOD")
        else:
            seut_report(self, context, 'ERROR', True, 'E006', col_type)

        return {'CANCELLED'}

    for idx, col in cols.items():
        result = check_collection(self, context, scene, col, True)
        if result == {'CONTINUE'}:

            if col.seut.col_type == 'lod' and idx - 1 in cols and cols[idx - 1].seut.lod_distance > col.seut.lod_distance:
                seut_report(self, context, 'ERROR', True, 'E011', col.name, cols[idx - 1].name)
                return {'CANCELLED'}

            for obj in col.objects:
                if check_uvms(self, context, obj) != {'CONTINUE'}:
                    return {'CANCELLED'}
                if scene.seut.sceneType == 'character' and check_weights(context, obj) is False:
                    return {'CANCELLED'}
            
            results = export_collection(self, context, col)
            if {'CANCELLED'} in results:
                return {'CANCELLED'}


def export_mwm(self, context):
    """Compiles to MWM from the previously exported temp files"""
    
    scene = context.scene
    preferences = get_preferences()
    path = get_abs_path(scene.seut.export_exportPath)
    materials_path = os.path.join(get_abs_path(preferences.asset_path), 'Materials')
    collections = get_collections(scene)

    settings = ExportSettings(scene, None)
    mwmfile = join(path, scene.seut.subtypeId + ".mwm")

    # This duplicates HKTs if none are defined for BS but one exists for main.
    hkts = []
    bses = []
    for f in os.listdir(path):
        if f is None:
            continue
        if os.path.isdir(f):
            continue

        if f == f"{scene.seut.subtypeId}.hkt" or (f"{scene.seut.subtypeId}_BS" in f and os.path.splitext(f)[1] == '.hkt'):
            hkts.append(f)

        elif f"{scene.seut.subtypeId}_BS" in f and os.path.splitext(f)[1] == '.fbx':
            bses.append(f)

    # If there are empty collision collections for BS collections, do not duplicate main's HKT for them.
    if 'hkt' in collections and not collections['hkt'] is None and collections['hkt'] != []:
        for col in collections['hkt']:
            if col.seut.ref_col is None:
                seut_report(self, context, 'INFO', False, 'I022', col.name)
                continue
            if col.seut.ref_col.seut.col_type == 'bs' and len(col.objects) == 0:
                bses.remove(f"{scene.seut.subtypeId}_BS{col.seut.ref_col.seut.type_index}.fbx")

    if len(hkts) == 1:
        if not "_BS" in os.path.basename(hkts[0]):
            for bs in bses:
                shutil.copyfile(os.path.join(path, hkts[0]), os.path.join(path, os.path.splitext(bs)[0] + '.hkt'))

    mwmbuilder(self, context, path, path, settings, mwmfile, materials_path)

    return {'FINISHED'}


def export_sbc(self, context):
    """Exports to SBC"""

    scene = context.scene
    collections = get_collections(scene)
    path_data = os.path.join(get_abs_path(scene.seut.mod_path), "Data")
    path_models = get_abs_path(scene.seut.export_exportPath)

    # Checks whether collection exists, is excluded or is empty
    result = check_collection(self, context, scene, collections['main'][0], False)
    if not result == {'CONTINUE'}:
        return result

    # 3 options: no file and no entry, file but no entry, file and entry

    # Create XML tree and add initial parameters.
    output = get_relevant_sbc(os.path.dirname(path_data), 'CubeBlocks', 'Definition', scene.seut.subtypeId)
    if output is not None:
        file_to_update = output[0]
        lines = output[1]
        start = output[2]
        end = output[3]
    
    if output is not None and start is not None and end is not None and scene.seut.export_sbc_type == 'update':
        update_sbc = True
        lines_entry = lines[start:end]
        definitions = None
        def_definition = None
    else:
        update_sbc = False
        lines_entry = ""
        definitions = ET.Element('Definitions')

    if not update_sbc:
        add_attrib(definitions, 'xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        add_attrib(definitions, 'xmlns:xsd', 'http://www.w3.org/2001/XMLSchema')

        cube_blocks = add_subelement(definitions, 'CubeBlocks')
        def_definition = add_subelement(cube_blocks, 'Definition')

        def_Id = add_subelement(def_definition, 'Id')
        add_subelement(def_Id, 'TypeId', 'CubeBlock')
        add_subelement(def_Id, 'SubtypeId', scene.seut.subtypeId)

        add_subelement(def_definition, 'DisplayName', '{LOC:DisplayName_' + scene.seut.subtypeId + '}')
        add_subelement(def_definition, 'Description', '{LOC:Description_' + scene.seut.subtypeId + '}')

    icon_path = 'Textures\GUI\Icons\AstronautBackpack.dds'
    icon_target_path = get_abs_path(os.path.join(scene.render.filepath, scene.seut.subtypeId + '.dds'))
    if (os.path.exists(icon_target_path) or os.path.exists(os.path.splitext(icon_target_path)[0] + '.png')) and icon_target_path.find('Textures') != -1:
        icon_path = os.path.join('Textures', icon_target_path.split('Textures\\')[1])
    lines_entry = update_add_subelement(def_definition, 'Icon', icon_path, update_sbc, lines_entry)

    medium_grid_scalar = 1.0 # default to doing nothing unless the 3to5 mode is detected

    if scene.seut.gridScale == 'large':
        lines_entry = update_add_subelement(def_definition, 'CubeSize', 'Large', update_sbc, lines_entry)
        grid_size = 2.5
        if (abs(scene.seut.export_rescaleFactor - 3) < 0.01): # floating point comparison
            medium_grid_scalar = 0.6 # Large grid block is going to be 3/5 of the expected size
    elif scene.seut.gridScale == 'small':
        lines_entry = update_add_subelement(def_definition, 'CubeSize', 'Small', update_sbc, lines_entry)
        grid_size = 0.5
        if (abs(scene.seut.export_rescaleFactor - 0.6) < 0.01): # floating point comparison
            medium_grid_scalar = 3.0 # Small grid block is going to be 3 times larger than expected
    
    def_Size = 'Size'
    if not update_sbc:
        add_subelement(def_definition, 'BlockTopology', 'TriangleMesh')
        def_Size = add_subelement(def_definition, 'Size')
    lines_entry = update_add_attrib(def_Size, 'x', round(scene.seut.bBox_X * medium_grid_scalar), update_sbc, lines_entry)
    lines_entry = update_add_attrib(def_Size, 'y', round(scene.seut.bBox_Z * medium_grid_scalar), update_sbc, lines_entry)   # This looks wrong but it's correct: Blender has different forward than SE.
    lines_entry = update_add_attrib(def_Size, 'z', round(scene.seut.bBox_Y * medium_grid_scalar), update_sbc, lines_entry)

    center_empty = None
    for obj in collections['main'][0].objects:
        if obj is not None and obj.type == 'EMPTY' and obj.name.startswith('Center'):
            center_empty = obj
            break

    if center_empty is not None:
        loc = convert_position_to_cell(context, grid_size, medium_grid_scalar, center_empty)

        def_Center = 'Center'
        if not update_sbc:
            def_Center = add_subelement(def_definition, 'Center')
        lines_entry = update_add_attrib(def_Center, 'x', loc[0], update_sbc, lines_entry)
        lines_entry = update_add_attrib(def_Center, 'y', loc[2], update_sbc, lines_entry)   # This looks wrong but it's correct: Blender has different forward than SE.
        lines_entry = update_add_attrib(def_Center, 'z', loc[1], update_sbc, lines_entry)

    if not update_sbc:
        def_ModelOffset = add_subelement(def_definition, 'ModelOffset')
        add_attrib(def_ModelOffset, 'x', 0)
        add_attrib(def_ModelOffset, 'y', 0)
        add_attrib(def_ModelOffset, 'z', 0)

    # Model
    lines_entry = update_add_subelement(def_definition, 'Model', os.path.join(create_relative_path(path_models, "Models"), scene.seut.subtypeId + '.mwm'), update_sbc, lines_entry)

    # Components
    if not update_sbc:
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

        if not update_sbc:
            # Wipe existing ones.
            for elem in def_definition:
                if elem.tag == 'MountPoints':
                    def_definition.remove(elem)

            def_Mountpoints = add_subelement(def_definition, 'MountPoints')

        else:
            def_Mountpoints = ET.Element('MountPoints')

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
                add_attrib(def_Mountpoint, 'b_StartX', "{:.2f}".format(round(start_x * medium_grid_scalar, 2)))
                add_attrib(def_Mountpoint, 'c_StartY', "{:.2f}".format(round(start_y * medium_grid_scalar, 2)))
                add_attrib(def_Mountpoint, 'd_EndX', "{:.2f}".format(round(end_x * medium_grid_scalar, 2)))
                add_attrib(def_Mountpoint, 'e_EndY', "{:.2f}".format(round(end_y * medium_grid_scalar, 2)))

                if area.properties_mask:
                    add_attrib(def_Mountpoint, 'f_PropertiesMask', str(area.properties_mask).lower())
                if area.exclusion_mask:
                    add_attrib(def_Mountpoint, 'g_ExclusionMask', str(area.exclusion_mask).lower())
                if not area.enabled:
                    add_attrib(def_Mountpoint, 'h_Enabled', str(area.enabled).lower())
                if area.default:
                    add_attrib(def_Mountpoint, 'i_Default', str(area.default).lower())
                if area.pressurized:
                    add_attrib(def_Mountpoint, 'j_PressurizedWhenOpen', str(area.pressurized).lower())

        if update_sbc:
            lines_entry = convert_back_xml(def_Mountpoints, 'MountPoints', lines_entry)
        
    # Build Stages
    if not collections['bs'] is None and len(collections['bs']) > 0:

        counter = 0
        for bs_col in collections['bs']:
            if len(bs_col.objects) > 0:
                counter += 1

        if counter > 0:
            if not update_sbc:
                def_BuildProgressModels = add_subelement(def_definition, 'BuildProgressModels')
            else:
                def_BuildProgressModels = ET.Element('BuildProgressModels')

            percentage = 1 / counter

            for bs in range(0, counter):
                def_BS_Model = ET.SubElement(def_BuildProgressModels, 'Model')

                # This makes sure the last build stage is set to upper bound 1.0
                if bs + 1 == counter:
                    add_attrib(def_BS_Model, 'BuildPercentUpperBound', "{:.2f}".format(1.0))
                else:
                    add_attrib(def_BS_Model, 'BuildPercentUpperBound', "{:.2f}".format((bs + 1) * percentage)[:4])

                add_attrib(def_BS_Model, 'File', os.path.join(create_relative_path(path_models, "Models"), scene.seut.subtypeId + '_BS' + str(bs + 1) + '.mwm'))
            
            if update_sbc:
                lines_entry = convert_back_xml(def_BuildProgressModels, 'BuildProgressModels', lines_entry)

    # BlockPairName
    if not update_sbc:
        add_subelement(def_definition, 'BlockPairName', scene.seut.subtypeId)

    # Mirroring
    if collections['mirroring'] != None:
        scene.seut.mirroringToggle == 'off'

    if scene.seut.mirroring_X != 'None':
        lines_entry = update_add_optional_subelement(def_definition, 'MirroringX', scene.seut.mirroring_X, update_sbc, lines_entry)
    elif update_sbc and scene.seut.mirroring_X == 'None' and get_subelement(lines_entry, 'MirroringX') != -1:
        lines_entry = lines_entry.replace(get_subelement(lines_entry, 'MirroringX'),"")

    if scene.seut.mirroring_Z != 'None':                                # This looks wrong but SE works with different Axi than Blender
        lines_entry = update_add_optional_subelement(def_definition, 'MirroringY', scene.seut.mirroring_Z, update_sbc, lines_entry)
    elif update_sbc and scene.seut.mirroring_Z == 'None' and get_subelement(lines_entry, 'MirroringY') != -1:
        lines_entry = lines_entry.replace(get_subelement(lines_entry, 'MirroringY'),"")

    if scene.seut.mirroring_Y != 'None':
        lines_entry = update_add_optional_subelement(def_definition, 'MirroringZ', scene.seut.mirroring_Y, update_sbc, lines_entry)
    elif update_sbc and scene.seut.mirroring_Y == 'None' and get_subelement(lines_entry, 'MirroringZ') != -1:
        lines_entry = lines_entry.replace(get_subelement(lines_entry, 'MirroringZ'),"")
    
    # If a MirroringScene is defined, set it in SBC but also set the reference to the base scene in the mirror scene SBC
    if scene.seut.mirroringScene is not None and scene.seut.mirroringScene.name in bpy.data.scenes:
        lines_entry = update_add_optional_subelement(def_definition, 'MirroringBlock', scene.seut.mirroringScene.seut.subtypeId, update_sbc, lines_entry)
    elif update_sbc and scene.seut.mirroringScene == 'None' and get_subelement(lines_entry, 'MirroringBlock') != -1:
        lines_entry = lines_entry.replace(get_subelement(lines_entry, 'MirroringBlock'),"")
    
    mirroringcenter_empty = None
    for obj in collections['main'][0].objects:
        if obj is not None and obj.type == 'EMPTY' and obj.name.startswith('MirroringCenter'):
            mirroringcenter_empty = obj
            break

    if mirroringcenter_empty is not None:
        loc = convert_position_to_cell(context, grid_size, medium_grid_scalar, mirroringcenter_empty)

        def_MirroringCenter = 'MirroringCenter'
        if not update_sbc:
            def_MirroringCenter = add_subelement(def_definition, 'MirroringCenter')
        lines_entry = update_add_attrib(def_MirroringCenter, 'x', loc[0], update_sbc, lines_entry)
        lines_entry = update_add_attrib(def_MirroringCenter, 'y', loc[2], update_sbc, lines_entry)   # This looks wrong but it's correct: Blender has different forward than SE.
        lines_entry = update_add_attrib(def_MirroringCenter, 'z', loc[1], update_sbc, lines_entry)

    # Write to file, place in export folder
    if not update_sbc:
        temp_string = ET.tostring(definitions, 'utf-8')
        try:
            temp_string.decode('ascii')
        except UnicodeDecodeError:
            seut_report(self, context, 'ERROR', True, 'E033')
        xml_string = xml.dom.minidom.parseString(temp_string)
        xml_formatted = xml_string.toprettyxml()
    
    else:
        xml_formatted = lines.replace(lines[start:end], lines_entry)
        xml_formatted = format_entry(xml_formatted)
        target_file = file_to_update

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

    if update_sbc:
        target_file = file_to_update
    else:
        filename = scene.seut.subtypeId
        target_file = os.path.join(path_data, "CubeBlocks", filename + ".sbc")
        if not os.path.exists(os.path.join(path_data, "CubeBlocks")):
            os.makedirs(os.path.join(path_data, "CubeBlocks"))
        
        # This covers the case where a file exists but the SBC export setting forces new file creation.
        counter = 1
        while os.path.exists(target_file):
            target_file = os.path.splitext(target_file)[0]
            split = target_file.split("_")
            try:
                number = int(split[len(split)-1]) + 1
                target_file = target_file[:target_file.rfind("_")]
                target_file = f"{target_file}_{number}.sbc"
            except:
                target_file = target_file + "_1.sbc"

    exported_xml = open(target_file, "w")
    exported_xml.write(xml_formatted)

    if not update_sbc:
        seut_report(self, context, 'INFO', False, 'I004', target_file)
    else:
        seut_report(self, context, 'INFO', False, 'I015', scene.seut.subtypeId, target_file)

    return {'FINISHED'}