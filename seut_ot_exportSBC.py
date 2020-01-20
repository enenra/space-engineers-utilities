import bpy
import os
import xml.etree.ElementTree as ET
import xml.dom.minidom

from bpy.types                       import Operator
from .seut_ot_recreateCollections    import SEUT_OT_RecreateCollections

class SEUT_OT_ExportSBC(Operator):
    """Exports to SBC"""
    bl_idname = "object.export_sbc"
    bl_label = "Export SBC"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """Exports the SBC file for a defined collection"""

        scene = context.scene
        collections = SEUT_OT_RecreateCollections.get_Collections()
        preferences = bpy.context.preferences.addons.get(__package__).preferences

        # self.report({'INFO'}, "SEUT: Running operator: 'object.export_sbc'")

        if preferences.pref_looseFilesExportFolder == '1' and scene.prop_export_exportPath == "" or os.path.exists(scene.prop_export_exportPath) == False:
            self.report({'ERROR'}, "SEUT: No export folder defined or export folder doesn't exist. (ExportSBC: 003)")
            return {'CANCELLED'}

        if preferences.pref_looseFilesExportFolder == '1' and scene.prop_export_exportPath.find("Models\\") == -1:
            self.report({'ERROR'}, "SEUT: Export folder does not contain 'Models\\'. Cannot be transformed into relative path. (014)")
            return {'CANCELLED'}

        if scene.prop_subtypeId == "":
            self.report({'ERROR'}, "SEUT: No SubtypeId set. (004)")
            return {'CANCELLED'}

        if collections['main'] == None:
            self.report({'ERROR'}, "SEUT: Collection 'Main' not found. Export not possible. (002)")
            return {'CANCELLED'}

        if len(collections['main'].objects) == 0:
            self.report({'ERROR'}, "SEUT: Collection 'Main' is empty. Export not possible. (005)")
            return {'CANCELLED'}

        if not scene.prop_export_sbc:
            self.report({'WARNING'}, "SEUT: 'SBC' is toggled off. SBC export skipped.")
            return {'CANCELLED'}

        if (len(collections['bs1'].objects) == 0 and len(collections['bs2'].objects) != 0) or (len(collections['bs2'].objects) == 0 and len(collections['bs3'].objects) != 0):
            self.report({'ERROR'}, "SEUT: Invalid Build Stage setup. Cannot have BS2 but no BS1, or BS3 but no BS2. (015)")
            return {'CANCELLED'}

        # Create XML tree and add initial parameters.
        definitions = ET.Element('Definitions')
        definitions.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        definitions.set('xmlns:xsd', 'http://www.w3.org/2001/XMLSchema')

        cubeBlocks = ET.SubElement(definitions, 'CubeBlocks')
        def_definition = ET.SubElement(cubeBlocks, 'Definition')
        
        def_Id = ET.SubElement(def_definition, 'Id')
        def_TypeId = ET.SubElement(def_Id, 'TypeId')
        def_TypeId.text = 'PLACEHOLDER'
        def_SubtypeId = ET.SubElement(def_Id, 'SubtypeId')
        def_SubtypeId.text = scene.prop_subtypeId

        def_DisplayName = ET.SubElement(def_definition, 'DisplayName')
        def_DisplayName.text = 'DisplayName_' + scene.prop_subtypeId
        def_Description = ET.SubElement(def_definition, 'Description')
        def_Description.text = 'Description_' + scene.prop_subtypeId
        
        def_Icon = ET.SubElement(def_definition, 'Icon')
        def_Icon.text = 'PLACEHOLDER'
        
        def_CubeSize = ET.SubElement(def_definition, 'CubeSize')
        if scene.prop_gridScale == '0': 
            def_CubeSize.text = 'Large'
        else:
            def_CubeSize.text = 'Small'
        
        def_BlockTopology = ET.SubElement(def_definition, 'BlockTopology')
        def_BlockTopology.text = 'TriangleMesh'

        def_Size = ET.SubElement(def_definition, 'Size')
        def_Size.set('x', str(scene.prop_bBox_X))
        def_Size.set('y', str(scene.prop_bBox_Y))
        def_Size.set('z', str(scene.prop_bBox_Z))

        def_ModelOffset = ET.SubElement(def_definition, 'ModelOffset')
        def_ModelOffset.set('x', '0')
        def_ModelOffset.set('y', '0')
        def_ModelOffset.set('z', '0')

        # Setting up the link to the MWM file.
        path = ""

        # If file is still startup file (hasn't been saved yet), it's not possible to derive a path from it.
        if not bpy.data.is_saved and preferences.pref_looseFilesExportFolder == '0':
            self.report({'ERROR'}, "SEUT: BLEND file must be saved before SBC can be exported to its directory. (008)")
            return
        else:
            if preferences.pref_looseFilesExportFolder == '0':
                path = os.path.dirname(bpy.data.filepath) + "\\"

            elif preferences.pref_looseFilesExportFolder == '1':
                path = bpy.path.abspath(scene.prop_export_exportPath)
        
        def_Model = ET.SubElement(def_definition, 'Model')
        def_Model.text = path + scene.prop_subtypeId + '.mwm'
        
        """
        def_Mountpoints = ET.SubElement(def_definition, 'Mountpoints')
        def_Mountpoint = ET.SubElement(def_Mountpoints, 'Mountpoint')
        def_Mountpoint.set('Side', 'PLACEHOLDER')
        def_Mountpoint.set('StartX', 'PLACEHOLDER')
        def_Mountpoint.set('StartY', 'PLACEHOLDER')
        def_Mountpoint.set('EndX', 'PLACEHOLDER')
        def_Mountpoint.set('EndY', 'PLACEHOLDER')
        def_Mountpoint.set('Default', 'PLACEHOLDER')
        """
        
        # Creating Build Stage references.
        def_BuildProgressModels = ET.SubElement(def_definition, 'BuildProgressModels')

        counter = 0
        if collections['bs1'] != None and len(collections['bs1'].objects) > 0:
            counter += 1
            
        if collections['bs2'] != None and len(collections['bs2'].objects) > 0:
            counter += 1
            
        if collections['bs3'] != None and len(collections['bs3'].objects) > 0:
            counter += 1
            
        percentage = 1 / counter

        for bs in counter:
            def_BS_Model = ET.SubElement(def_BuildProgressModels, 'Model')

            # This makes sure the last build stage is set to upper bound 1.0
            if bs + 1 == counter:
                def_BS_Model.set('BuildPercentUpperBound', str(1.0))
            else:
                def_BS_Model.set('BuildPercentUpperBound', str((bs + 1) * percentage))

            def_BS_Model.set('File', path + scene.prop_subtypeId + '_BS' + str(bs + 1) + '.mwm')


        # Write to file, place in export folder
        xmlString = xml.dom.minidom.parseString(ET.tostring(definitions))
        xmlFormatted = xmlString.toprettyxml()

        filename = scene.prop_subtypeId

        exportedXML = open(path + filename + ".sbc", "w")
        exportedXML.write(xmlFormatted)
        self.report({'INFO'}, "SEUT: '%s.sbc' has been created." % (path + filename))

        return {'FINISHED'}