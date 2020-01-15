import bpy
import os
import xml.etree.ElementTree as ET
import xml.dom.minidom

from bpy.types                       import Operator
from .seut_ot_recreateCollections    import SEUT_OT_RecreateCollections

class SEUT_OT_Export(Operator):
    """Exports all enabled file types and collections"""
    bl_idname = "object.export"
    bl_label = "Export"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        scene = context.scene
        preferences = bpy.context.preferences.addons.get(__package__).preferences

        # Debug
        self.report({'DEBUG'}, "SEUT: OT Export executed.")

        if scene.prop_export_exportPath == "":
            self.report({'ERROR'}, "SEUT: No export folder defined. (003)")
            return {'CANCELLED'}

        if scene.prop_export_exportPath.find("Models\\") == -1:
            self.report({'ERROR'}, "SEUT: Export folder does not contain 'Models\\'. Cannot be transformed into relative path. (014)")
            return {'CANCELLED'}

        if scene.prop_subtypeId == "":
            self.report({'ERROR'}, "SEUT: No SubtypeId set. (004)")
            return {'CANCELLED'}
        
        # Call all the individual export operators
        bpy.ops.object.export_main()
        bpy.ops.object.export_bs()
        bpy.ops.object.export_lod()

        # HKT and SBC export are the only two filetypes those operators handle so I check for enabled here.
        if scene.prop_export_hkt:
            bpy.ops.object.export_hkt()

        if scene.prop_export_sbc:
            bpy.ops.object.export_sbc()
        
        # Once I implement MWM export, make it adhere to export folder - may need to check for it again?

        return {'FINISHED'}


    def export_XML(self, context, collection):
        """Exports the XML file for a defined collection"""

        scene = context.scene
        collections = SEUT_OT_RecreateCollections.get_Collections()
        preferences = bpy.context.preferences.addons.get(__package__).preferences

        # Create XML tree and add initial parameters.
        model = ET.Element('Model')
        model.set('Name', 'Default')

        paramCentered = ET.SubElement(model, 'Parameter')
        paramCentered.set('Name', 'Centered')
        paramCentered.text = 'false'

        paramRescaleFactor = ET.SubElement(model, 'Parameter')
        paramRescaleFactor.set('Name', 'RescaleFactor')
        paramRescaleFactor.text = str(context.scene.prop_export_rescaleFactor)

        paramRescaleToLengthInMeters = ET.SubElement(model, 'Parameter')
        paramRescaleToLengthInMeters.set('Name', 'RescaleToLengthInMeters')
        paramRescaleToLengthInMeters.text = 'false'
        
        # Currently no support for the other material parameters - are those even needed anymore?

        # Iterate through all materials in the file
        for mat in bpy.data.materials:
            if mat == None:
                continue
            
            # mat is a local material.
            elif mat.library == None:

                # If the material is not part of a linked library, I have to account for the possibility that it is a leftover material from import.
                # Those do get cleaned up, but only after the BLEND file is saved, closed and reopened. That may not have happened.
                isUnique = False
                for mtl in bpy.data.materials:
                    # There is a material with its name in a linked library but override is turned on.
                    if mtl.library != None and mtl.name == mat.name and mat.seut.overrideMatLib == True:
                        print("check: mat:" + mat.name + ", mtl: " + mtl.name + ", override: " + str(mat.seut.overrideMatLib))
                        isUnique = True
                    # There is a material with its name in a linked library and override is turned off.
                    if mtl.library != None and mtl.name == mat.name and mat.seut.overrideMatLib == False:
                        print("check2: mat:" + mat.name + ", mtl: " + mtl.name + ", override: " + str(mat.seut.overrideMatLib))
                        isUnique = False
                    # There is no material with its name in a linked library.
                    elif mtl.library == None and mat.library == None and mtl.name == mat.name:
                        print("check3: mat:" + mat.name + ", mtl: " + mtl.name + ", override: " + str(mat.seut.overrideMatLib))
                        isUnique = True
                
                if isUnique:
                    matEntry = ET.SubElement(model, 'Material')
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
                        model.remove(matEntry)

            elif mat.library != None:
                matRef = ET.SubElement(model, 'MaterialRef')
                matRef.set('Name', mat.name)
                
        
        # Only add LODs to XML if exporting the main collection, the LOD collections exist and are not empty.
        if collection == collections['main']:
            
            lod1Printed = False
            lod2Printed = False

            if collections['lod1'] == None or len(collections['lod1'].objects) == 0:
                self.report({'INFO'}, "SEUT: Collection 'LOD1' not found or empty. Skipping.")
            else:
                lod1 = ET.SubElement(model, 'LOD')
                lod1.set('Distance', str(scene.prop_export_lod1Distance))
                lod1Model = ET.SubElement(lod1, 'Model')
                lod1Model.text = scene.prop_subtypeId + '_LOD1'
                lod1Printed = True

            if collections['lod2'] == None or len(collections['lod2'].objects) == 0:
                self.report({'INFO'}, "SEUT: Collection 'LOD2' not found or empty. Skipping.")
            else:
                if lod1Printed: 
                    lod2 = ET.SubElement(model, 'LOD')
                    lod2.set('Distance', str(scene.prop_export_lod2Distance))
                    lod2Model = ET.SubElement(lod2, 'Model')
                    lod2Model.text = scene.prop_subtypeId + '_LOD2'
                    lod2Printed = True
                else:
                    self.report({'ERROR'}, "SEUT: LOD2 cannot be set if LOD1 is not. (006)")

            if collections['lod3'] == None or len(collections['lod3'].objects) == 0:
                self.report({'INFO'}, "SEUT: Collection 'LOD3' not found or empty. Skipping.")
            else:
                if lod1Printed and lod2Printed:
                    lod3 = ET.SubElement(model, 'LOD')
                    lod3.set('Distance', str(scene.prop_export_lod3Distance))
                    lod3Model = ET.SubElement(lod3, 'Model')
                    lod3Model.text = scene.prop_subtypeId + '_LOD3'
                else:
                    self.report({'ERROR'}, "SEUT: LOD3 cannot be set if LOD1 or LOD2 is not. (006)")


        # Create file with subtypename + collection name and write string to it
        xmlString = xml.dom.minidom.parseString(ET.tostring(model))
        xmlFormatted = xmlString.toprettyxml()

        if collection == collections['main']:
            filename = scene.prop_subtypeId
        else:
            filename = scene.prop_subtypeId + '_' + collection.name

        path = ""

        # If file is still startup file (hasn't been saved yet), it's not possible to derive a path from it.
        if not bpy.data.is_saved and preferences.pref_looseFilesExportFolder == '0':
            self.report({'ERROR'}, "SEUT: BLEND file must be saved before XML can be exported to its directory. (008)")
            return
        else:
            if preferences.pref_looseFilesExportFolder == '0':
                path = os.path.dirname(bpy.data.filepath) + "\\"

            elif preferences.pref_looseFilesExportFolder == '1':
                path = bpy.path.abspath(scene.prop_export_exportPath)

        exportedXML = open(path + filename + ".xml", "w")
        exportedXML.write(xmlFormatted)
        self.report({'INFO'}, "SEUT: '%s.xml' has been created." % (path + filename))

        return

    
    def export_FBX(self, context, collection):
        """Exports the FBX file for a defined collection"""

        scene = context.scene
        collections = SEUT_OT_RecreateCollections.get_Collections()
        preferences = bpy.context.preferences.addons.get(__package__).preferences

        # Determining the directory to export to.
        if collection == collections['main']:
            filename = scene.prop_subtypeId
        else:
            filename = scene.prop_subtypeId + '_' + collection.name

        path = ""

        # If file is still startup file (hasn't been saved yet), it's not possible to derive a path from it.
        if not bpy.data.is_saved and preferences.pref_looseFilesExportFolder == '0':
            self.report({'ERROR'}, "SEUT: BLEND file must be saved before FBX can be exported to its directory. (008)")
            return
        else:
            if preferences.pref_looseFilesExportFolder == '0':
                path = os.path.dirname(bpy.data.filepath) + "\\"

            elif preferences.pref_looseFilesExportFolder == '1':
                path = bpy.path.abspath(scene.prop_export_exportPath)
        
        # Exporting the collection.
        # I can only export the currently active collection, so I need to set the target collection to active (for which I have to link it for some reason),
        # then export, then unlink. User won't see it and it shouldn't make a difference.
        bpy.context.scene.collection.children.link(collection)
        layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]
        bpy.context.view_layer.active_layer_collection = layer_collection

        bpy.ops.export_scene.fbx(filepath=path + filename + ".fbx", use_active_collection=True)

        bpy.context.scene.collection.children.unlink(collection)
        self.report({'INFO'}, "SEUT: '%s.fbx' has been created." % (path + filename))

        return