import bpy
import os
import xml.etree.ElementTree as ET
import xml.dom.minidom

from bpy.types      import Operator
from collections    import OrderedDict

from ..seut_ot_mirroring            import SEUT_OT_Mirroring
from ..seut_ot_mountpoints          import SEUT_OT_Mountpoints
from ..seut_ot_recreate_collections import get_collections
from ..seut_errors                  import check_export, check_collection, seut_report

class SEUT_OT_ExportSBC(Operator):
    """Exports to SBC"""
    bl_idname = "object.export_sbc"
    bl_label = "Export SBC"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        collections = get_collections(context.scene)
        return collections['main'] is not None

    def execute(self, context):
        """Exports the SBC file for a defined collection"""

        # Checks export path and whether SubtypeId exists
        result = check_export(self, context)
        if not result == {'CONTINUE'}:
            return result
        
        result = SEUT_OT_ExportSBC.export_SBC(self, context)

        return result
    
    def export_SBC(self, context):
        """Exports the SBC file for a defined collection"""

        scene = context.scene
        collections = get_collections(scene)
        addon = __package__[:__package__.find(".")]
        preferences = bpy.context.preferences.addons.get(addon).preferences

        if not scene.seut.export_sbc:
            print("SEUT Info: 'SBC' is toggled off. SBC export skipped.")
            return {'FINISHED'}
        
        if scene.seut.sceneType == 'subpart' or scene.seut.sceneType == 'character' or scene.seut.sceneType == 'character_animation':
            print("SEUT Info: Scene '" + scene.name + "' is of type '" + scene.seut.sceneType + "'. SBC export skipped.")
            return {'FINISHED'}

        # Checks whether collection exists, is excluded or is empty
        result = check_collection(self, context, scene, collections['main'], False)
        if not result == {'CONTINUE'}:
            return result

        if collections['bs1'] is not None and collections['bs2'] is not None:
            if (len(collections['bs1'].objects) == 0 and len(collections['bs2'].objects) != 0) or (len(collections['bs2'].objects) == 0 and len(collections['bs3'].objects) != 0):
                seut_report(self, context, 'ERROR', True, 'E015', 'BS')
                return {'CANCELLED'}

        if collections['bs2'] is not None and collections['bs3'] is not None:
            if (len(collections['bs2'].objects) == 0 and len(collections['bs3'].objects) != 0):
                seut_report(self, context, 'ERROR', True, 'E015', 'BS')
                return {'CANCELLED'}

        # Create XML tree and add initial parameters.
        definitions = ET.Element('Definitions')
        definitions.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        definitions.set('xmlns:xsd', 'http://www.w3.org/2001/XMLSchema')

        cubeBlocks = ET.SubElement(definitions, 'CubeBlocks')
        def_definition = ET.SubElement(cubeBlocks, 'Definition')
        
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

        centerEmpty = None
        for obj in collections['main'].objects:
            if obj is not None and obj.type == 'EMPTY' and obj.name == 'Center':
                centerEmpty = obj

        if centerEmpty is not None:                
            def_Center = ET.SubElement(def_definition, 'Center')
            def_Center.set('x', str(round(centerEmpty.location.x / gridSize)))
            def_Center.set('y', str(round(centerEmpty.location.z / gridSize)))   # This looks wrong but it's correct: Blender has different forward than SE.
            def_Center.set('z', str(round(centerEmpty.location.y / gridSize)))

        def_ModelOffset = ET.SubElement(def_definition, 'ModelOffset')
        def_ModelOffset.set('x', '0')
        def_ModelOffset.set('y', '0')
        def_ModelOffset.set('z', '0')

        # Setting up the link to the MWM file.
        path = os.path.abspath(bpy.path.abspath(scene.seut.export_exportPath)) + "\\"
        
        offset = path.find("Models\\")

        def_Model = ET.SubElement(def_definition, 'Model')
        def_Model.text=path[offset:] + scene.seut.subtypeId + '.mwm'

        # Basic components
        def_Components = ET.SubElement(def_definition, 'Components')
        def_Component = ET.SubElement(def_Components, 'Component')
        def_Component.set('Subtype', 'SteelPlate')
        def_Component.set('Count', '10')

        def_CriticalComponent = ET.SubElement(def_definition, 'CriticalComponent')
        def_CriticalComponent.set('Subtype', 'SteelPlate')
        def_CriticalComponent.set('Index', '0')

        if scene.seut.subtypeId == "":
            scene.seut.subtypeId = scene.name
        tag = ' (' + scene.seut.subtypeId + ')'

        if 'Mountpoints' + tag in bpy.data.collections:
            SEUT_OT_Mountpoints.saveMountpointData(context, bpy.data.collections['Mountpoints' + tag])
        
        if len(scene.seut.mountpointAreas) != 0:

            if scene.seut.gridScale == 'small':
                scale = 0.5
            else:
                scale = 2.5

            bboxX = scene.seut.bBox_X * scale
            bboxY = scene.seut.bBox_Y * scale
            bboxZ = scene.seut.bBox_Z * scale

            def_Mountpoints = ET.SubElement(def_definition, 'MountPoints')

            for area in scene.seut.mountpointAreas:
                if area is not None:

                    def_Mountpoint = ET.SubElement(def_Mountpoints, 'MountPoint')

                    sideName = area.side.capitalize()

                    if area.side == 'front' or area.side == 'back':
                        if area.x + (area.xDim / 2) - (bboxX / 2) > 0:
                            startX = 0.0
                        else:
                            startX = abs(area.x + (area.xDim / 2) - (bboxX / 2)) / scale

                        if area.y + (area.yDim / 2) - (bboxZ / 2) > 0:
                            startY = 0.0
                        else:
                            startY = abs(area.y + (area.yDim / 2) - (bboxZ / 2)) / scale

                        endX = abs(area.x - (area.xDim / 2) - (bboxX / 2)) / scale
                        endY = abs(area.y - (area.yDim / 2) - (bboxZ / 2)) / scale

                        if endX > scene.seut.bBox_X:
                            endX = scene.seut.bBox_X
                        if endY > scene.seut.bBox_Z:
                            endY = scene.seut.bBox_Z

                    elif area.side == 'left' or area.side == 'right':
                        if area.x + (area.xDim / 2) - (bboxY / 2) > 0:
                            startX = 0.0
                        else:
                            startX = abs(area.x + (area.xDim / 2) - (bboxY / 2)) / scale

                        if area.y + (area.yDim / 2) - (bboxZ / 2) > 0:
                            startY = 0.0
                        else:
                            startY = abs(area.y + (area.yDim / 2) - (bboxZ / 2)) / scale
                            
                        endX = abs(area.x - (area.xDim / 2) - (bboxY / 2)) / scale
                        endY = abs(area.y - (area.yDim / 2) - (bboxZ / 2)) / scale

                        if endX > scene.seut.bBox_Y:
                            endX = scene.seut.bBox_Y
                        if endY > scene.seut.bBox_Z:
                            endY = scene.seut.bBox_Z

                    elif area.side == 'top' or area.side == 'bottom':
                        if area.x + (area.xDim / 2) - (bboxX / 2) > 0:
                            startX = 0.0
                        else:
                            startX = abs(area.x + (area.xDim / 2) - (bboxX / 2)) / scale

                        if area.y + (area.yDim / 2) - (bboxY / 2) > 0:
                            startY = 0.0
                        else:
                            startY = abs(area.y + (area.yDim / 2) - (bboxY / 2)) / scale

                        endX = abs(area.x - (area.xDim / 2) - (bboxX / 2)) / scale
                        endY = abs(area.y - (area.yDim / 2) - (bboxY / 2)) / scale

                        if endX > scene.seut.bBox_X:
                            endX = scene.seut.bBox_X
                        if endY > scene.seut.bBox_Y:
                            endY = scene.seut.bBox_Y

                    # Need to do this to prevent ET from auto-rearranging keys.
                    def_Mountpoint.set('a_Side', sideName)
                    def_Mountpoint.set('b_StartX', str(round(startX, 2)))
                    def_Mountpoint.set('c_StartY', str(round(startY, 2)))
                    def_Mountpoint.set('d_EndX', str(round(endX, 2)))
                    def_Mountpoint.set('e_EndY', str(round(endY, 2)))
                    if area.default:
                        def_Mountpoint.set('f_Default', str(area.default).lower())
                    if area.pressurized:
                        def_Mountpoint.set('g_PressurizedWhenOpen', str(area.pressurized).lower())

        
        # Creating Build Stage references.
        if collections['bs1'] is not None or collections['bs2'] is not None or collections['bs3'] is not None:

            counter = 0
            if collections['bs1'] != None and len(collections['bs1'].objects) > 0:
                counter += 1
                
            if collections['bs2'] != None and len(collections['bs2'].objects) > 0:
                counter += 1
                
            if collections['bs3'] != None and len(collections['bs3'].objects) > 0:
                counter += 1
            
            if counter != 0:
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
        for empty in scene.objects:
            if empty.type == 'EMPTY' and (empty.name == 'Mirroring X' or empty.name == 'Mirroring Y' or empty.name == 'Mirroring Z'):
                SEUT_OT_Mirroring.saveRotationToProps(self, context, empty)

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
        tempString = ET.tostring(definitions, 'utf-8')
        try:
            tempString.decode('ascii')
        except UnicodeDecodeError:
            seut_report(self, context, 'ERROR', True, 'E033')
        xmlString = xml.dom.minidom.parseString(tempString)
        xmlFormatted = xmlString.toprettyxml()

        # Fixing the entries
        xmlFormatted = xmlFormatted.replace("a_Side", "Side")
        xmlFormatted = xmlFormatted.replace("b_StartX", "StartX")
        xmlFormatted = xmlFormatted.replace("c_StartY", "StartY")
        xmlFormatted = xmlFormatted.replace("d_EndX", "EndX")
        xmlFormatted = xmlFormatted.replace("e_EndY", "EndY")
        xmlFormatted = xmlFormatted.replace("f_Default", "Default")
        xmlFormatted = xmlFormatted.replace("g_PressurizedWhenOpen", "PressurizedWhenOpen")

        filename = scene.seut.subtypeId

        exportedXML = open(path + filename + ".sbc", "w")
        exportedXML.write(xmlFormatted)

        print("SEUT Info: '%s.sbc' has been created." % (path + filename))

        return {'FINISHED'}