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
from ..seut_preferences             import get_addon_version
from ..seut_collections             import get_collections
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

    print("\n============================================================ Exporting Scene '" + scene.name + "' with SEUT " + str(get_addon_version()) + ".")

    current_area = prep_context(context)

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
    if materials_path == "" or os.path.isdir(materials_path) == False:
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
        else:
            scene.seut.export_rescaleFactor = 1.0

        if scene.seut.export_exportPath.find("/small/") != -1:
            scene.seut.export_exportPath = scene.seut.export_exportPath.replace("/small/", "/large/")
        
        export_all(self, context)
    
    # Exports small grid scenes
    if scene.seut.export_smallGrid:
        scene.seut.gridScale = 'small'
        scene.seut.subtypeId = correct_for_export_type(scene, scene.seut.subtypeId)

        if grid_scale == 'large':
            scene.seut.export_rescaleFactor = 0.2
        else:
            scene.seut.export_rescaleFactor = 1.0

        if scene.seut.export_exportPath.find("/large/") != -1:
            scene.seut.export_exportPath = scene.seut.export_exportPath.replace("/large/", "/small/")
        
        export_all(self, context)

    # Resetting the variables
    if scene.seut.export_largeGrid and scene.seut.export_smallGrid:
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
        
        if obj.parent is None:
            unparented_objects += 1
        
        # Check for missing UVMs (this might not be 100% reliable)
        if check_uvms(obj) != {'CONTINUE'}:
            return {'CANCELLED'}  
    
    # Check for armatures being present in collection
    if not found_armatures and (scene.seut.sceneType == 'character' or scene.seut.sceneType == 'character_animation'):
        seut_report(self, context, 'WARNING', True, 'W008', scene.seut.sceneType)
    if found_armatures and not (scene.seut.sceneType == 'character' or scene.seut.sceneType == 'character_animation'):
        seut_report(self, context, 'WARNING', True, 'W009', scene.seut.sceneType)
    
    # Check for unparented objects
    if unparented_objects > 1:
        seut_report(self, context, 'ERROR', True, 'E031')
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

    # Checks whether collection exists, is excluded or is empty
    result = check_collection(self, context, scene, collections['hkt'], True)
    if not result == {'CONTINUE'}:
        return result

    # Check for availability of Havok SFM
    result = check_toolpath(self, context, preferences.havok_path, "Havok Standalone Filter Manager", "hctStandAloneFilterManager.exe")
    if not result == {'CONTINUE'}:
        return result
    
    for obj in collections['hkt'].objects:

        # Check for unapplied modifiers
        if len(obj.modifiers) > 0:
            seut_report(self, context, 'ERROR', True, 'E034', obj.name)
            return {'CANCELLED'}
        
        # Apply Rigid Body
        context.view_layer.objects.active = obj
        # bpy.ops.object.transform_apply(location = True, scale = True, rotation = True) # This runs on all objects instead of just the active one for some reason. Breaks when there's instanced subparts.
        bpy.ops.rigidbody.object_add(type='ACTIVE')
    
    # Check if max amount of collision objects is exceeded
    if len(collections['hkt'].objects) > 16:
        seut_report(self, context, 'ERROR', True, 'E022', len(collections['hkt'].objects))
        return {'CANCELLED'}

    # FBX export via Custom FBX Importer
    fbx_hkt_file = join(path, scene.seut.subtypeId + ".hkt.fbx")
    hkt_file = join(path, scene.seut.subtypeId + ".hkt")
    
    export_to_fbxfile(settings, scene, fbx_hkt_file, collections['hkt'].objects, ishavokfbxfile=True)

    # Then create the HKT file.
    process_hktfbx_to_fbximporterhkt(context, settings, fbx_hkt_file, hkt_file)
    process_fbximporterhkt_to_final_hkt_for_mwm(self, context, scene, path, settings, hkt_file, hkt_file)
        
    return {'FINISHED'}


def export_bs(self, context):
    """Exports Build Stage collections"""

    scene = context.scene
    collections = get_collections(scene)
    preferences = get_preferences()

    # Checks whether collections exists, are excluded or are empty
    bs1_valid = False
    result = check_collection(self, context, scene, collections['bs1'], True)
    if result == {'CONTINUE'}:
        bs1_valid = True

    bs2_valid = False
    result = check_collection(self, context, scene, collections['bs2'], True)
    if result == {'CONTINUE'}:
        bs2_valid = True

    bs3_valid = False
    result = check_collection(self, context, scene, collections['bs3'], True)
    if result == {'CONTINUE'}:
        bs3_valid = True

    if (not bs1_valid and bs2_valid) or (not bs2_valid and bs3_valid):
        seut_report(self, context, 'ERROR', True, 'E015', 'BS')
        return {'CANCELLED'}
    
    # Check for missing UVMs (this might not be 100% reliable)
    if bs1_valid:
        for obj in collections['bs1'].objects:
            if check_uvms(obj) != {'CONTINUE'}:
                return {'CANCELLED'}
    
    if bs2_valid:
        for obj in collections['bs2'].objects:
            if check_uvms(obj) != {'CONTINUE'}:
                return {'CANCELLED'}
    
    if bs3_valid:
        for obj in collections['bs3'].objects:
            if check_uvms(obj) != {'CONTINUE'}:
                return {'CANCELLED'}

    if bs1_valid:
        export_collection(self, context, collections['bs1'])
    if bs2_valid:
        export_collection(self, context, collections['bs2'])
    if bs3_valid:
        export_collection(self, context, collections['bs3'])
    
    return {'FINISHED'}


def export_lod(self, context):
    """Exports LOD collections"""

    scene = context.scene
    collections = get_collections(scene)
    preferences = get_preferences()

    # Checks whether collections exists, are excluded or are empty
    lod1_valid = False
    result = check_collection(self, context, scene, collections['lod1'], True)
    if result == {'CONTINUE'}:
        lod1_valid = True

    lod2_valid = False
    result = check_collection(self, context, scene, collections['lod2'], True)
    if result == {'CONTINUE'}:
        lod2_valid = True

    lod3_valid = False
    result = check_collection(self, context, scene, collections['lod3'], True)
    if result == {'CONTINUE'}:
        lod3_valid = True

    bs_lod_valid = False
    result = check_collection(self, context, scene, collections['bs_lod'], True)
    if result == {'CONTINUE'}:
        bs_lod_valid = True

    if (not lod1_valid and lod2_valid) or (not lod2_valid and lod3_valid):
        seut_report(self, context, 'ERROR', True, 'E015', 'LOD')
        return {'CANCELLED'}

    # Checks whether LOD distances are valid
    if scene.seut.export_lod1Distance > scene.seut.export_lod2Distance or scene.seut.export_lod2Distance > scene.seut.export_lod3Distance:
        seut_report(self, context, 'ERROR', True, 'E011')
        return {'CANCELLED'}
    
    # Check for missing UVMs (this might not be 100% reliable)
    if lod1_valid:
        for obj in collections['lod1'].objects:
            if check_uvms(obj) != {'CONTINUE'}:
                return {'CANCELLED'}

    if lod2_valid:
        for obj in collections['lod2'].objects:
            if check_uvms(obj) != {'CONTINUE'}:
                return {'CANCELLED'}
    
    if lod3_valid:
        for obj in collections['lod3'].objects:
            if check_uvms(obj) != {'CONTINUE'}:
                return {'CANCELLED'}
    
    if bs_lod_valid:
        for obj in collections['bs_lod'].objects:
            if check_uvms(obj) != {'CONTINUE'}:
                return {'CANCELLED'}

    if lod1_valid:
        export_collection(self, context, collections['lod1'])  
    if lod2_valid:
        export_collection(self, context, collections['lod2'])
    if lod3_valid:
        export_collection(self, context, collections['lod3'])
    if bs_lod_valid:
        export_collection(self, context, collections['bs_lod'])
    
    return {'FINISHED'}


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
            delete_loose_files(path)

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

    # Checks whether collections exists, are excluded or are empty
    bs1_valid = False
    result = check_collection(self, context, scene, collections['bs1'], True)
    if result == {'CONTINUE'}:
        bs1_valid = True

    bs2_valid = False
    result = check_collection(self, context, scene, collections['bs2'], True)
    if result == {'CONTINUE'}:
        bs2_valid = True

    bs3_valid = False
    result = check_collection(self, context, scene, collections['bs3'], True)
    if result == {'CONTINUE'}:
        bs3_valid = True

    if (not bs1_valid and bs2_valid) or (not bs2_valid and bs3_valid):
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
    def_DisplayName.text = 'DisplayName_' + scene.seut.subtypeId
    def_Description = ET.SubElement(def_definition, 'Description')
    def_Description.text = 'Description_' + scene.seut.subtypeId
    
    def_Icon = ET.SubElement(def_definition, 'Icon')
    def_Icon.text = 'Textures\GUI\Icons\AstronautBackpack.dds'
    
    def_CubeSize = ET.SubElement(def_definition, 'CubeSize')

    if scene.seut.gridScale == 'large':
        def_CubeSize.text = 'Large'
        gridSize = 2.5
    elif scene.seut.gridScale == 'small':
        def_CubeSize.text = 'Small'
        gridSize = 0.5
    
    def_BlockTopology = ET.SubElement(def_definition, 'BlockTopology')
    def_BlockTopology.text = 'TriangleMesh'

    def_Size = ET.SubElement(def_definition, 'Size')
    def_Size.set('x', str(scene.seut.bBox_X))
    def_Size.set('y', str(scene.seut.bBox_Z))   # This looks wrong but it's correct: Blender has different forward than SE.
    def_Size.set('z', str(scene.seut.bBox_Y))

    center_empty = None
    for obj in collections['main'].objects:
        if obj is not None and obj.type == 'EMPTY' and obj.name == 'Center':
            center_empty = obj
            break

    if center_empty is not None:                
        def_Center = ET.SubElement(def_definition, 'Center')
        def_Center.set('x', str(round(center_empty.location.x / gridSize)))
        def_Center.set('y', str(round(center_empty.location.z / gridSize)))   # This looks wrong but it's correct: Blender has different forward than SE.
        def_Center.set('z', str(round(center_empty.location.y / gridSize)))

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

        if scene.seut.gridScale == 'small':
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
                def_Mountpoint.set('b_StartX', str(round(start_x, 2)))
                def_Mountpoint.set('c_StartY', str(round(start_y, 2)))
                def_Mountpoint.set('d_EndX', str(round(end_x, 2)))
                def_Mountpoint.set('e_EndY', str(round(end_y, 2)))

                if area.default:
                    def_Mountpoint.set('f_Default', str(area.default).lower())
                if area.pressurized:
                    def_Mountpoint.set('g_PressurizedWhenOpen', str(area.pressurized).lower())

    
    # Build Stages
    if collections['bs1'] is not None or collections['bs2'] is not None or collections['bs3'] is not None:

        counter = 0
        if collections['bs1'] != None and len(collections['bs1'].objects) > 0:
            counter += 1
        if collections['bs2'] != None and len(collections['bs2'].objects) > 0:
            counter += 1
        if collections['bs3'] != None and len(collections['bs3'].objects) > 0:
            counter += 1

        if counter > 0:
            def_BuildProgressModels = ET.SubElement(def_definition, 'BuildProgressModels')

            percentage = 1 / counter

            for bs in range(0, counter):
                def_BS_Model = ET.SubElement(def_BuildProgressModels, 'Model')

                # This makes sure the last build stage is set to upper bound 1.0
                if bs + 1 == counter:
                    def_BS_Model.set('BuildPercentUpperBound', str(1.0))
                else:
                    def_BS_Model.set('BuildPercentUpperBound', str((bs + 1) * percentage)[:4])

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
    xml_formatted = xml_formatted.replace("f_Default", "Default")
    xml_formatted = xml_formatted.replace("g_PressurizedWhenOpen", "PressurizedWhenOpen")

    filename = scene.seut.subtypeId

    exported_xml = open(path + filename + ".sbc", "w")
    exported_xml.write(xml_formatted)

    seut_report(self, context, 'INFO', False, 'I004', path + filename + ".sbc")

    return {'FINISHED'}