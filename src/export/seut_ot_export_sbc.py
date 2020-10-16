import bpy
import os
import xml.etree.ElementTree as ET
import xml.dom.minidom

from bpy.types      import Operator
from collections    import OrderedDict

from ..seut_ot_recreate_collections import get_collections
from ..seut_errors                  import check_export, check_collection, seut_report, get_abs_path


class SEUT_OT_ExportSBC(Operator):
    """Exports to SBC"""
    bl_idname = "object.export_sbc"
    bl_label = "Export to SBC"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        collections = get_collections(context.scene)
        return collections['main'] is not None


    def execute(self, context):
        """Calls the function to export to SBC"""

        # Checks export path and whether SubtypeId exists
        result = check_export(self, context)
        if not result == {'CONTINUE'}:
            return result
        
        result = export_sbc(self, context)

        return result
    
    
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
        return {'INVALID_BS_SETUP'}

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
    offset = path.find("Models\\")
    def_Model = ET.SubElement(def_definition, 'Model')
    def_Model.text=path[offset:] + scene.seut.subtypeId + '.mwm'

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

                def_BS_Model.set('File', path[offset:] + scene.seut.subtypeId + '_BS' + str(bs + 1) + '.mwm')

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