import bpy
import os
import xml.etree.ElementTree as ET
import xml.dom.minidom

from bpy.types      import Operator

from ..seut_ot_mirroring            import SEUT_OT_Mirroring
from ..seut_ot_mountpoints          import SEUT_OT_Mountpoints
from ..seut_ot_recreateCollections  import SEUT_OT_RecreateCollections
from ..seut_errors                  import errorExportGeneral

class SEUT_OT_ExportSBC(Operator):
    """Exports to SBC"""
    bl_idname = "object.export_sbc"
    bl_label = "Export SBC"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        collections = SEUT_OT_RecreateCollections.getCollections(context.scene)
        return collections['main'] is not None

    def execute(self, context):
        """Exports the SBC file for a defined collection"""

        print("SEUT Info: Running operator: ------------------------------------------------------------------ 'object.export_sbc'")

        # Checks export path and whether SubtypeId exists
        result = errorExportGeneral(self, context)
        if not result == {'CONTINUE'}:
            return result
        
        result = SEUT_OT_ExportSBC.export_SBC(self, context)
        
        print("SEUT Info: Finished operator: ----------------------------------------------------------------- 'object.export_sbc'")

        return result
    
    def export_SBC(self, context):
        """Exports the SBC file for a defined collection"""

        scene = context.scene
        collections = SEUT_OT_RecreateCollections.getCollections(scene)
        addon = __package__[:__package__.find(".")]
        preferences = bpy.context.preferences.addons.get(addon).preferences

        if not scene.seut.export_sbc:
            print("SEUT Info: 'SBC' is toggled off. SBC export skipped.")
            return {'FINISHED'}
        
        if context.scene.seut.sceneType == 'subpart':
            print("SEUT Info: Scene '" + scene.name + "' is of type 'Subpart'. SBC export skipped.")
            return {'FINISHED'}

        if collections['bs1'] is not None and collections['bs2'] is not None:
            if (len(collections['bs1'].objects) == 0 and len(collections['bs2'].objects) != 0) or (len(collections['bs2'].objects) == 0 and len(collections['bs3'].objects) != 0):
                self.report({'ERROR'}, "SEUT: Invalid Build Stage setup. Cannot have BS2 but no BS1. (015)")
                return {'CANCELLED'}

        if collections['bs2'] is not None and collections['bs3'] is not None:
            if (len(collections['bs2'].objects) == 0 and len(collections['bs3'].objects) != 0):
                self.report({'ERROR'}, "SEUT: Invalid Build Stage setup. Cannot have BS3 but no BS2. (015)")
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
        path = bpy.path.abspath(scene.seut.export_exportPath)
        
        offset = path.find("Models\\")

        def_Model = ET.SubElement(def_definition, 'Model')
        def_Model.text=path[offset:] + scene.seut.subtypeId + '.mwm'

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

            def_Mountpoints = ET.SubElement(def_definition, 'Mountpoints')

            for area in scene.seut.mountpointAreas:
                if area is not None:

                    def_Mountpoint = ET.SubElement(def_Mountpoints, 'Mountpoint')

                    sideName = area.side.capitalize()

                    if area.side == 'front' or area.side == 'back':
                        if area.x + (area.xDim / 2) - (bboxX / 2) > 0:
                            startX = 0.0
                        else:
                            startX = 100 / bboxX * abs(area.x + (area.xDim / 2) - (bboxX / 2))

                        if area.y + (area.yDim / 2) - (bboxZ / 2) > 0:
                            startY = 0.0
                        else:
                            startY = 100 / bboxZ * abs(area.y + (area.yDim / 2) - (bboxZ / 2))

                        endX = 100 / bboxX * abs(area.x - (area.xDim / 2) - (bboxX / 2))
                        endY = 100 / bboxZ * abs(area.y - (area.yDim / 2) - (bboxZ / 2))

                    elif area.side == 'left' or area.side == 'right':
                        if area.x + (area.xDim / 2) - (bboxY / 2) > 0:
                            startX = 0.0
                        else:
                            startX = 100 / bboxY * abs(area.x + (area.xDim / 2) - (bboxY / 2))

                        if area.y + (area.yDim / 2) - (bboxZ / 2) > 0:
                            startY = 0.0
                        else:
                            startY = 100 / bboxZ * abs(area.y + (area.yDim / 2) - (bboxZ / 2))
                            
                        endX = 100 / bboxY * abs(area.x - (area.xDim / 2) - (bboxY / 2))
                        endY = 100 / bboxZ * abs(area.y - (area.yDim / 2) - (bboxZ / 2))

                    elif area.side == 'top' or area.side == 'bottom':
                        if area.x + (area.xDim / 2) - (bboxX / 2) > 0:
                            startX = 0.0
                        else:
                            startX = 100 / bboxX * abs(area.x + (area.xDim / 2) - (bboxX / 2))

                        if area.y + (area.yDim / 2) - (bboxY / 2) > 0:
                            startY = 0.0
                        else:
                            startY = 100 / bboxY * abs(area.y + (area.yDim / 2) - (bboxY / 2))

                        endX = 100 / bboxX * abs(area.x - (area.xDim / 2) - (bboxX / 2))
                        endY = 100 / bboxY * abs(area.y - (area.yDim / 2) - (bboxY / 2))
                    
                    if endX > 100:
                        endX = 100.0
                    if endY > 100:
                        endY = 100.0

                    def_Mountpoint.set('Side', sideName)
                    def_Mountpoint.set('StartX', str(round(startX, 2)))
                    def_Mountpoint.set('StartY', str(round(startY, 2)))
                    def_Mountpoint.set('EndX', str(round(endX, 2)))
                    def_Mountpoint.set('EndY', str(round(endY, 2)))

                    if area.side == 'bottom':
                        def_Mountpoint.set('Default', 'true')
        
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

        # Mirroring
        for empty in scene.objects:
            if empty.type == 'EMPTY' and (empty.name == 'Mirroring X' or empty.name == 'Mirroring Y' or empty.name == 'Mirroring Z'):
                SEUT_OT_Mirroring.saveRotationToProps(self, context, empty)

        if scene.seut.mirroring_X != 'None':
            def_MirroringX = ET.SubElement(def_definition, 'MirroringX')
            def_MirroringX.text = scene.seut.mirroring_X
        if scene.seut.mirroring_Y != 'None':
            def_MirroringY = ET.SubElement(def_definition, 'MirroringY')
            def_MirroringY.text = scene.seut.mirroring_Y
        if scene.seut.mirroring_Z != 'None':
            def_MirroringZ = ET.SubElement(def_definition, 'MirroringZ')
            def_MirroringZ.text = scene.seut.mirroring_Z
        
        # If a MirroringScene is defined, set it in SBC but also set the reference to the base scene in the mirror scene SBC
        if scene.seut.mirroringScene is not None and scene.seut.mirroringScene.name in bpy.data.scenes:
            def_MirroringBlock = ET.SubElement(def_definition, 'MirroringBlock')
            def_MirroringBlock.text = scene.seut.mirroringScene.seut.subtypeId

        elif scene.seut.sceneType == 'mirror':
            for scn in bpy.data.scenes:
                if scn.seut.mirroringScene == scene:
                    def_MirroringBlock = ET.SubElement(def_definition, 'MirroringBlock')
                    def_MirroringBlock.text = scn.seut.subtypeId


        # Write to file, place in export folder
        xmlString = xml.dom.minidom.parseString(ET.tostring(definitions))
        xmlFormatted = xmlString.toprettyxml()

        filename = scene.seut.subtypeId

        exportedXML = open(path + filename + ".sbc", "w")
        exportedXML.write(xmlFormatted)
        self.report({'INFO'}, "SEUT: '%s.sbc' has been created." % (path + filename))

        return {'FINISHED'}