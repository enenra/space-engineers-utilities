import bpy
import os
import xml.etree.ElementTree as ET
import xml.dom.minidom

from bpy.types  import Operator

class SEUT_OT_ExportMaterials(Operator):
    """Export local materials to Materials.xml file"""
    bl_idname = "scene.export_materials"
    bl_label = "Export Materials to XML"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        if not bpy.data.is_saved:
            self.report({'ERROR'}, "SEUT: BLEND file must be saved before export. (008)")
            print("SEUT Error: BLEND file must be saved before export. (008)")
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

                # These properties are only relevant for GLASS
                if mat.seut.technique == 'GLASS' or mat.seut.technique == 'ALPHA_MASKED':
                    if mat.seut.specularIntensity != 0:
                        matSpecIntensity = ET.SubElement(matEntry, 'Parameter')
                        matSpecIntensity.set('Name', 'SpecularIntensity')
                        matSpecIntensity.text = str(mat.seut.specularIntensity)

                    if mat.seut.specularPower != 0:
                        matSpecPower = ET.SubElement(matEntry, 'Parameter')
                        matSpecPower.set('Name', 'SpecularPower')
                        matSpecPower.text = str(mat.seut.specularPower)
                    
                    if mat.seut.diffuseColor[0] != 0 and mat.seut.diffuseColor[1] != 0 and mat.seut.diffuseColor[2] != 0:
                        matDiffColorX = ET.SubElement(matEntry, 'Parameter')
                        matDiffColorX.set('Name', 'DiffuseColorX')
                        matDiffColorX.text = str(int(mat.seut.diffuseColor[0] * 255))

                        matDiffColorY = ET.SubElement(matEntry, 'Parameter')
                        matDiffColorY.set('Name', 'DiffuseColorY')
                        matDiffColorY.text = str(int(mat.seut.diffuseColor[1] * 255))

                        matDiffColorZ = ET.SubElement(matEntry, 'Parameter')
                        matDiffColorZ.set('Name', 'DiffuseColorZ')
                        matDiffColorZ.text = str(int(mat.seut.diffuseColor[2] * 255))

                    if mat.seut.diffuseTexture != "":
                        matDiffTexture = ET.SubElement(matEntry, 'Parameter')
                        matDiffTexture.set('Name', 'DiffuseTexture')
                        matDiffTexture.text = mat.seut.diffuseTexture
                
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
                        self.report({'ERROR'}, "SEUT: 'CM' texture filepath in local material '%s' does not contain 'Textures\\'. Cannot be transformed into relative path. (007)" % (mat.name))
                    else:
                        matCM = ET.SubElement(matEntry, 'Parameter')
                        matCM.set('Name', 'ColorMetalTexture')
                        matCM.text = images['cm'].filepath[offset:]
                
                # _ng NormalGloss texture
                if images['ng'] == None:
                    self.report({'WARNING'}, "SEUT: No 'NG' texture or node found for local material '%s'. Skipping." % (mat.name))
                else:
                    offset = images['ng'].filepath.find("Textures\\")
                    if offset == -1:
                        self.report({'ERROR'}, "SEUT: 'NG' texture filepath in local material '%s' does not contain 'Textures\\'. Cannot be transformed into relative path. (007)" % (mat.name))
                    else:
                        matNG = ET.SubElement(matEntry, 'Parameter')
                        matNG.set('Name', 'NormalGlossTexture')
                        matNG.text = images['ng'].filepath[offset:]
                
                # _add AddMaps texture
                if images['add'] == None:
                    self.report({'WARNING'}, "SEUT: No 'ADD' texture or node found for local material '%s'. Skipping." % (mat.name))
                else:
                    offset = images['add'].filepath.find("Textures\\")
                    if offset == -1:
                        self.report({'ERROR'}, "SEUT: 'ADD' texture filepath in local material '%s' does not contain 'Textures\\'. Cannot be transformed into relative path. (007)" % (mat.name))
                    else:
                        matADD = ET.SubElement(matEntry, 'Parameter')
                        matADD.set('Name', 'AddMapsTexture')
                        matADD.text = images['add'].filepath[offset:]
                
                # _alphamask Alphamask texture
                if images['am'] == None:
                    self.report({'WARNING'}, "SEUT: No 'ALPHAMASK' texture or node found for local material '%s'. Skipping." % (mat.name))
                else:
                    offset = images['am'].filepath.find("Textures\\")
                    if offset == -1:
                        self.report({'ERROR'}, "SEUT: 'ALPHAMASK' texture filepath in local material '%s' does not contain 'Textures\\'. Cannot be transformed into relative path. (007)" % (mat.name))
                    else:
                        matAM = ET.SubElement(matEntry, 'Parameter')
                        matAM.set('Name', 'AlphamaskTexture')
                        matAM.text = images['am'].filepath[offset:]

                # If no textures are added to the material, remove the entry again.
                if images['cm'] == None and images['ng'] == None and images['add'] == None and images['am'] == None:
                    self.report({'INFO'}, "SEUT: Local material '%s' does not contain any valid textures. Skipping." % (mat.name))
                    materials.remove(matEntry)
                    
        # Create file with subtypename + collection name and write string to it
        xmlString = xml.dom.minidom.parseString(ET.tostring(materials))
        xmlFormatted = xmlString.toprettyxml()
        
        offset = bpy.path.basename(bpy.context.blend_data.filepath).find(".blend")
        filename = bpy.path.basename(bpy.context.blend_data.filepath)[:offset]
        
        exportedXML = open(bpy.path.abspath('//') + filename + ".xml", "w")
        exportedXML.write(xmlFormatted)
        self.report({'INFO'}, "SEUT: '%s.xml' has been created." % (bpy.path.abspath('//') + filename))

        return {'FINISHED'}
