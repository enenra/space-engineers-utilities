import bpy
import os
import xml.etree.ElementTree as ET
import xml.dom.minidom

from bpy.types  import Operator

from ..seut_errors  import report_error

class SEUT_OT_ExportMaterials(Operator):
    """Export local materials to Materials.xml file"""
    bl_idname = "scene.export_materials"
    bl_label = "Export Materials to Library"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        if not bpy.data.is_saved:
            report_error(self, context, True, 'E008')
            return {'CANCELLED'}

        return SEUT_OT_ExportMaterials.exportMaterials(self, context)

    
    def exportMaterials(self, context):
        """Export local materials to Materials.xml file"""
        
        scene = context.scene

        materials = ET.Element('MaterialsLib')
        materials.set('Name', 'Default Materials')

        for mat in bpy.data.materials:
            if mat.library is None:
                matEntry = ET.SubElement(materials, 'Material')
                matEntry.set('Name', mat.name)

                matTechnique = ET.SubElement(matEntry, 'Parameter')
                matTechnique.set('Name', 'Technique')
                matTechnique.text = mat.seut.technique

                if mat.seut.facing != 'None':
                    matFacing = ET.SubElement(matEntry, 'Parameter')
                    matFacing.set('Name', 'Facing')
                    matFacing.text = mat.seut.facing
                    
                if mat.seut.windScale != 0:
                    matWindScale = ET.SubElement(matEntry, 'Parameter')
                    matWindScale.set('Name', 'WindScale')
                    matWindScale.text = str(mat.seut.windScale)
                    
                if mat.seut.windFrequency != 0:
                    matWindFrequency = ET.SubElement(matEntry, 'Parameter')
                    matWindFrequency.set('Name', 'WindFrequency')
                    matWindFrequency.text = str(mat.seut.windFrequency)
                
                # Iterate through all image textures in material and register relevant ones to dictionary.
                images = {
                    'cm': None,
                    'ng': None,
                    'add': None,
                    'am': None
                    }

                if mat.node_tree is not None:
                    for node in mat.node_tree.nodes:
                        if node.type == 'TEX_IMAGE':
                            if node.name == 'CM':
                                images['cm'] = node.image
                            if node.name == 'NG':
                                images['ng'] = node.image
                            if node.name == 'ADD':
                                images['add'] = node.image
                            if node.name == 'ALPHAMASK':
                                images['am'] = node.image

                # Used to create the relative paths for the textures.
                offset = 0

                # _cm ColorMask texture
                if images['cm'] == None:
                    self.report({'WARNING'}, "SEUT: No 'CM' texture or node found for local material '%s'. Skipping." % (mat.name))
                else:
                    offset = images['cm'].filepath.find("Textures\\")
                    if offset == -1:
                        report_error(self, context, True, 'E007', 'CM', mat.name)
                    else:
                        matCM = ET.SubElement(matEntry, 'Parameter')
                        matCM.set('Name', 'ColorMetalTexture')
                        matCM.text = os.path.splitext(images['cm'].filepath[offset:])[0] + ".dds"
                
                # _ng NormalGloss texture
                if images['ng'] == None:
                    self.report({'WARNING'}, "SEUT: No 'NG' texture or node found for local material '%s'. Skipping." % (mat.name))
                else:
                    offset = images['ng'].filepath.find("Textures\\")
                    if offset == -1:
                        report_error(self, context, True, 'E007', 'NG', mat.name)
                    else:
                        matNG = ET.SubElement(matEntry, 'Parameter')
                        matNG.set('Name', 'NormalGlossTexture')
                        matNG.text = os.path.splitext(images['ng'].filepath[offset:])[0] + ".dds"
                
                # _add AddMaps texture
                if images['add'] == None:
                    self.report({'WARNING'}, "SEUT: No 'ADD' texture or node found for local material '%s'. Skipping." % (mat.name))
                else:
                    offset = images['add'].filepath.find("Textures\\")
                    if offset == -1:
                        report_error(self, context, True, 'E007', 'ADD', mat.name)
                    else:
                        matADD = ET.SubElement(matEntry, 'Parameter')
                        matADD.set('Name', 'AddMapsTexture')
                        matADD.text = os.path.splitext(images['add'].filepath[offset:])[0] + ".dds"
                
                # _alphamask Alphamask texture
                if images['am'] == None:
                    self.report({'WARNING'}, "SEUT: No 'ALPHAMASK' texture or node found for local material '%s'. Skipping." % (mat.name))
                else:
                    offset = images['am'].filepath.find("Textures\\")
                    if offset == -1:
                        report_error(self, context, True, 'E007', 'ALPHAMASK', mat.name)
                    else:
                        matAM = ET.SubElement(matEntry, 'Parameter')
                        matAM.set('Name', 'AlphamaskTexture')
                        matAM.text = os.path.splitext(images['am'].filepath[offset:])[0] + ".dds"

                # If no textures are added to the material, remove the entry again.
                if images['cm'] == None and images['ng'] == None and images['add'] == None and images['am'] == None:
                    self.report({'INFO'}, "SEUT: Local material '%s' does not contain any valid textures. Skipping." % (mat.name))
                    materials.remove(matEntry)
                    
        # Create file with subtypename + collection name and write string to it
        tempString = ET.tostring(materials, 'utf-8')
        try:
            tempString.decode('ascii')
        except UnicodeDecodeError:
            report_error(self, context, False, 'E033')
        xmlString = xml.dom.minidom.parseString(tempString)
        xmlFormatted = xmlString.toprettyxml()
        
        offset = bpy.path.basename(bpy.context.blend_data.filepath).find(".blend")
        filename = bpy.path.basename(bpy.context.blend_data.filepath)[:offset]

        # This culls the MatLb_ from the filename
        if filename.find("MatLib_") != -1:
            filename = filename[7:]
        
        exportedXML = open(bpy.path.abspath('//') + filename + ".xml", "w")
        exportedXML.write(xmlFormatted)
        self.report({'INFO'}, "SEUT: '%s.xml' has been created." % (bpy.path.abspath('//') + filename))

        return {'FINISHED'}
