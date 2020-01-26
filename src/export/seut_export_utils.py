import bpy
import os
import glob
import subprocess
import xml.etree.ElementTree as ET
import xml.dom.minidom

from os.path                        import join
from mathutils                      import Matrix	
from bpy_extras.io_utils            import axis_conversion, ExportHelper

from .havok.seut_havok_fbx          import save_single
from ..seut_ot_recreateCollections  import SEUT_OT_RecreateCollections
from ..seut_utils                   import linkSubpartScene, unlinkSubpartScene

def export_XML(self, context, collection):
    """Exports the XML file for a defined collection"""

    scene = context.scene
    collections = SEUT_OT_RecreateCollections.get_Collections(scene)
    addon = __package__[:__package__.find(".")]
    preferences = bpy.context.preferences.addons.get(addon).preferences

    # Create XML tree and add initial parameters.
    model = ET.Element('Model')
    model.set('Name', 'Default')

    paramCentered = ET.SubElement(model, 'Parameter')
    paramCentered.set('Name', 'Centered')
    paramCentered.text = 'false'

    paramRescaleFactor = ET.SubElement(model, 'Parameter')
    paramRescaleFactor.set('Name', 'RescaleFactor')
    paramRescaleFactor.text = str(context.scene.seut.export_rescaleFactor)

    paramRescaleToLengthInMeters = ET.SubElement(model, 'Parameter')
    paramRescaleToLengthInMeters.set('Name', 'RescaleToLengthInMeters')
    paramRescaleToLengthInMeters.text = 'false'
    
    path = ""

    if not bpy.data.is_saved and preferences.looseFilesExportFolder == '0':
        self.report({'ERROR'}, "SEUT: BLEND file must be saved before Models can be exported. (021)")
        print("SEUT Error: BLEND file must be saved before Models can be exported. (021)")
        return {'CANCELLED'}
    else:
        if preferences.looseFilesExportFolder == '0':
            path = os.path.dirname(bpy.data.filepath) + "\\"

        elif preferences.looseFilesExportFolder == '1':
            path = bpy.path.abspath(scene.seut.export_exportPath)

    # Currently no support for the other material parameters - are those even needed anymore?

    # Iterate through all materials in the file
    for mat in bpy.data.materials:
        if mat == None:
            continue
        
        # This ensures that the material presets used internally are not written to the XML.
        if mat.name[:5] == 'SMAT_':
            continue
        
        # mat is a local material.
        elif mat.library == None:

            # If the material is not part of a linked library, I have to account for the possibility that it is a leftover material from import.
            # Those do get cleaned up, but only after the BLEND file is saved, closed and reopened. That may not have happened.
            isUnique = False
            for mtl in bpy.data.materials:
                # There is a material with its name in a linked library but override is turned on.
                if mtl.library != None and mtl.name == mat.name and mat.seut.overrideMatLib == True:
                    isUnique = True
                # There is a material with its name in a linked library and override is turned off.
                if mtl.library != None and mtl.name == mat.name and mat.seut.overrideMatLib == False:
                    isUnique = False
                # There is no material with its name in a linked library.
                elif mtl.library == None and mat.library == None and mtl.name == mat.name:
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
                    model.remove(matEntry)

        elif mat.library != None:
            matRef = ET.SubElement(model, 'MaterialRef')
            matRef.set('Name', mat.name)
            
    
    # Only add LODs to XML if exporting the main collection, the LOD collections exist and are not empty.
    if collection == collections['main']:
        
        lod1Printed = False
        lod2Printed = False

        if collections['lod1'] == None or len(collections['lod1'].objects) == 0:
            self.report({'INFO'}, "SEUT: Collection 'LOD1' not found or empty. Skipping XML entry.")
        else:
            lod1 = ET.SubElement(model, 'LOD')
            lod1.set('Distance', str(scene.seut.export_lod1Distance))
            lod1Model = ET.SubElement(lod1, 'Model')
            lod1Model.text = path[path.find("Models\\"):] + scene.seut.subtypeId + '_LOD1'
            lod1Printed = True

        if collections['lod2'] == None or len(collections['lod2'].objects) == 0:
            self.report({'INFO'}, "SEUT: Collection 'LOD2' not found or empty. Skipping XML entry.")
        else:
            if lod1Printed: 
                lod2 = ET.SubElement(model, 'LOD')
                lod2.set('Distance', str(scene.seut.export_lod2Distance))
                lod2Model = ET.SubElement(lod2, 'Model')
                lod2Model.text = path[path.find("Models\\"):] + scene.seut.subtypeId + '_LOD2'
                lod2Printed = True
            else:
                self.report({'ERROR'}, "SEUT: LOD2 cannot be set if LOD1 is not. (006)")

        if collections['lod3'] == None or len(collections['lod3'].objects) == 0:
            self.report({'INFO'}, "SEUT: Collection 'LOD3' not found or empty. Skipping XML entry.")
        else:
            if lod1Printed and lod2Printed:
                lod3 = ET.SubElement(model, 'LOD')
                lod3.set('Distance', str(scene.seut.export_lod3Distance))
                lod3Model = ET.SubElement(lod3, 'Model')
                lod3Model.text = path[path.find("Models\\"):] + scene.seut.subtypeId + '_LOD3'
            else:
                self.report({'ERROR'}, "SEUT: LOD3 cannot be set if LOD1 or LOD2 is not. (006)")

    if collection == collections['bs1'] or collection == collections['bs2'] or collection == collections['bs3']:
        if collections['bs_lod'] == None or len(collections['bs_lod'].objects) == 0:
            self.report({'INFO'}, "SEUT: Collection 'BS_LOD' not found or empty. Skipping XML entry.")
        else:
            bs_lod = ET.SubElement(model, 'LOD')
            bs_lod.set('Distance', str(scene.seut.export_bs_lodDistance))
            bs_lodModel = ET.SubElement(bs_lod, 'Model')
            bs_lodModel.text = path[path.find("Models\\"):] + scene.seut.subtypeId + '_BS_LOD'

    # Create file with subtypename + collection name and write string to it
    xmlString = xml.dom.minidom.parseString(ET.tostring(model))
    xmlFormatted = xmlString.toprettyxml()
    
    fileType = collection.name[:collection.name.find(" (")]
    
    if collection == collections['main']:
        filename = scene.seut.subtypeId
    else:
        filename = scene.seut.subtypeId + '_' + fileType

    exportedXML = open(path + filename + ".xml", "w")
    exportedXML.write(xmlFormatted)
    self.report({'INFO'}, "SEUT: '%s.xml' has been created." % (path + filename))

    return {'FINISHED'}


def export_model_FBX(self, context, collection):
    """Exports the FBX file for a defined collection"""

    scene = context.scene
    depsgraph = context.evaluated_depsgraph_get()
    addon = __package__[:__package__.find(".")]
    preferences = bpy.context.preferences.addons.get(addon).preferences
    collections = SEUT_OT_RecreateCollections.get_Collections(scene)
    settings = ExportSettings(scene, depsgraph)

    # Determining the directory to export to.
    fileType = collection.name[:collection.name.find(" (")]

    if collection == collections['main']:
        filename = scene.seut.subtypeId
    else:
        filename = scene.seut.subtypeId + '_' + fileType

    # If file is still startup file (hasn't been saved yet), it's not possible to derive a path from it.
    path = ""

    if not bpy.data.is_saved and preferences.looseFilesExportFolder == '0':
        self.report({'ERROR'}, "SEUT: BLEND file must be saved before FBX can be exported to its directory. (008)")
        return
    else:
        if preferences.looseFilesExportFolder == '0':
            path = os.path.dirname(bpy.data.filepath) + "\\"

        elif preferences.looseFilesExportFolder == '1':
            path = bpy.path.abspath(scene.seut.export_exportPath)
    
    # Exporting the collection.
    # I can only export the currently active collection, so I need to set the target collection to active (for which I have to link it for some reason),
    # then export, then unlink. User won't see it and it shouldn't make a difference.
    bpy.context.scene.collection.children.link(collection)
    layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]
    bpy.context.view_layer.active_layer_collection = layer_collection
    
    # Unlink all subparts parented to an empty
    for emptyObj in collection.objects:
        if 'file' in emptyObj:
            unlinkSubpartScene(emptyObj)

    for objMat in bpy.data.materials:
        if objMat is not None and objMat.node_tree is not None:
            prepMatForExport(self, context, objMat)

    # This is the actual call to make an FBX file.
    fbxfile = join(path, filename + ".fbx")
    export_to_fbxfile(settings, scene, fbxfile, collection.objects, ishavokfbxfile=False)

    for objMat in bpy.data.materials:
        if objMat is not None and objMat.node_tree is not None:
            removeExportDummiesFromMat(self, context, objMat)
    
    # Relink all subparts to empties
    for emptyObj in collection.objects:
        if 'file' in emptyObj and emptyObj.seut.linkedScene is not "":
            linkSubpartScene(self, scene, emptyObj, emptyObj.seut.linkedScene)

    bpy.context.scene.collection.children.unlink(collection)
    self.report({'INFO'}, "SEUT: '%s.fbx' has been created." % (path + filename))

    return {'FINISHED'}


def prepMatForExport(self, context, material):
    """Switches material around so that SE can properly read it"""
    
    # See if relevant nodes already exist
    dummyShaderNode = None
    dummyImageNode = None
    dummyImage = None
    materialOutput = None

    for node in material.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED' and node.name == 'EXPORT_DUMMY':
            dummyShaderNode = node
        elif node.type == 'TEX_IMAGE' and node.name == 'DUMMY_IMAGE':
            dummyImageNode = node
        elif node.type == 'OUTPUT_MATERIAL':
            materialOutput = node

    # Iterate through images to find the dummy image
    for img in bpy.data.images:
        if img.name == 'DUMMY':
            dummyImage = img

    # If no, create it and DUMMY image node, and link them up
    if dummyImageNode is None:
        dummyImageNode = material.node_tree.nodes.new('ShaderNodeTexImage')
        dummyImageNode.name = 'DUMMY_IMAGE'
        dummyImageNode.label = 'DUMMY_IMAGE'

    if dummyImage is None:
        dummyImage = bpy.data.images.new('DUMMY', 1, 1)

    if dummyShaderNode is None:
        dummyShaderNode = material.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
        dummyShaderNode.name = 'EXPORT_DUMMY'
        dummyShaderNode.label = 'EXPORT_DUMMY'
    
    if materialOutput is None:
        materialOutput = material.node_tree.nodes.new('ShaderNodeOutputMaterial')
        material.seut.nodeLinkedToOutputName = ""
    # This allows the reestablishment of connections after the export is complete.
    else:
        if materialOutput.inputs[0].links[0].from_node.name is not None:
            material.seut.nodeLinkedToOutputName = materialOutput.inputs[0].links[0].from_node.name

    # link nodes, add image to node
    material.node_tree.links.new(dummyImageNode.outputs[0], dummyShaderNode.inputs[0])
    material.node_tree.links.new(dummyShaderNode.outputs[0], materialOutput.inputs[0])
    dummyImageNode.image = dummyImage

    return


def removeExportDummiesFromMat(self, context, material):
    """Removes the dummy nodes from the material again after export"""

    materialOutput = None
    nodeLinkedToOutput = None

    # Remove dummy nodes - do I need to remove the links too?
    # Image can stay, it's 1x1 px so nbd
    for node in material.node_tree.nodes:
        if node.type == 'TEX_IMAGE' and node.name == 'DUMMY_IMAGE':
            material.node_tree.nodes.remove(node)
        elif node.type == 'BSDF_PRINCIPLED' and node.name == 'EXPORT_DUMMY':
            material.node_tree.nodes.remove(node)

        elif node.type == 'OUTPUT_MATERIAL':
            materialOutput = node
        elif node.name == material.seut.nodeLinkedToOutputName:
            nodeLinkedToOutput = node
    
    # link the node group back to output
    if nodeLinkedToOutput is not None:
        material.node_tree.links.new(nodeLinkedToOutput.outputs[0], materialOutput.inputs[0])

    return


# STOLLIE: Standard output error operator class for catching error return codes.
class StdoutOperator():
    def report(self, type, message):
        print(message)

# STOLLIE: Assigning of above class to a global constant.
STDOUT_OPERATOR = StdoutOperator()

# STOLLIE: Processes subprocesss tool error messages, e.g. FBXImporter/HavokTool/MWMBuilder.
class MissbehavingToolError(subprocess.SubprocessError):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message

# STOLLIE: Returns a tools path from the user preferences config, e.g. FBXImporter/HavokTool/MWMBuilder.
def tool_path(propertyName, displayName, toolPath=None):
    """Gets path to tool from user preferences.

    Returns:
    toolPath
    """
    if toolPath is None:
        # STOLLIE: This is referencing the folder name the addon is stored in.
        addon = __package__[:__package__.find(".")]
        toolPath = getattr(bpy.context.preferences.addons.get(addon).preferences, propertyName)

    if toolPath is None:
        raise FileNotFoundError("%s is not configured", (displayName))

    toolPath = os.path.normpath(bpy.path.abspath(toolPath))
    if os.path.isfile(toolPath) is None:
        raise FileNotFoundError("%s: no such file %s" % (displayName, toolPath))

    return toolPath

# STOLLIE: Called by other methods to write to a log file when an errors occur.
def write_to_log(logfile, content, cmdline=None, cwd=None, loglines=[]):
    with open(logfile, 'wb') as log: # wb params here represent writing/create file and binary mode.
        if cwd:
            str = "Running from: %s \n" % (cwd)
            log.write(str.encode('utf-8'))

        if cmdline:
            str = "Command: %s \n" % (" ".join(cmdline))
            log.write(str.encode('utf-8'))

        for line in loglines:
            log.write(line.encode('utf-8'))
            log.write(b"\n")

        log.write(content)

def delete_loose_files(path):
    fileRemovalList = [fileName for fileName in glob.glob(path + "*.*") if "fbx" in fileName or
        "xml" in fileName or "hkt" in fileName or "log" in fileName]

    try:
        for fileName in fileRemovalList:
            os.remove(fileName)

    except EnvironmentError:
        self.report({'ERROR'}, "SEUT: Loose files file deletion failed. (020)")
        print("SEUT Error: File Deletion failed. (020)")

class ExportSettings:
    def __init__(self, scene, depsgraph, mwmDir=None):
        self.scene = scene # ObjectSource.getObjects() uses .utils.scene() instead
        self.depsgraph = depsgraph
        self.operator = STDOUT_OPERATOR
        self.isLogToolOutput = True
        
        # set on first access, see properties below
        self._fbximporter = None
        self._havokfilter = None
        self._mwmbuilder = None

        if scene.seut.export_deleteLooseFiles:
            self.isLogToolOutput = False
        
    @property
    def fbximporter(self):
        if self._fbximporter == None:
            self._fbximporter = tool_path('fbxImporterPath', 'Custom FBX Importer')
        return self._fbximporter

    @property
    def havokfilter(self):
        if self._havokfilter == None:
            self._havokfilter = tool_path('havokPath', 'Havok Standalone Filter Tool')
        return self._havokfilter

    @property
    def mwmbuilder(self):
        if self._mwmbuilder == None:
            self._mwmbuilder = tool_path('mwmbPath', 'MWM Builder')
        return self._mwmbuilder

    def callTool(self, cmdline, logfile=None, cwd=None, successfulExitCodes=[0], loglines=[], logtextInspector=None):
        try:
            out = subprocess.check_output(cmdline, cwd=cwd, stderr=subprocess.STDOUT, shell=True)
            if self.isLogToolOutput and logfile:
                write_to_log(logfile, out, cmdline=cmdline, cwd=cwd, loglines=loglines)
            if logtextInspector is not None:
                logtextInspector(out)

        except subprocess.CalledProcessError as e:
            if self.isLogToolOutput and logfile:
                write_to_log(logfile, e.output, cmdline=cmdline, cwd=cwd, loglines=loglines)
            if e.returncode not in successfulExitCodes:
                raise
    
    def __getitem__(self, key): # makes all attributes available for parameter substitution
        if not type(key) is str or key.startswith('_'):
            raise KeyError(key)
        try:
            value = getattr(self, key)
            if value is None or type(value) is _FUNCTION_TYPE:
                raise KeyError(key)
            return value
        except AttributeError:
            raise KeyError(key)

# HARAG: UP = 'Y'
# HARAG: FWD = 'Z'
# HARAG: MATRIX_NORMAL = axis_conversion(to_forward=FWD, to_up=UP).to_4x4()
# HARAG: MATRIX_SCALE_DOWN = Matrix.Scale(0.2, 4) * MATRIX_NORMAL
def export_to_fbxfile(settings: ExportSettings, scene, filepath, objects, ishavokfbxfile = False, kwargs = None):	
    kwargs = {	
        'global_matrix': Matrix(),
        'apply_unit_scale': True,
        'global_scale': 0.1, # STOLLIE: Is 1.0 in Blender Source
        'apply_scale_options': 'FBX_SCALE_NONE',
        'axis_up': 'Y',	 # STOLLIE: Normally a Z in Blender source.	Y aligns correctly in SE.
        'axis_forward': '-Z', # STOLLIE: Normally a Y in Blender source. -Z is correct forward.
        'context_objects': objects, #STOLLIE: Is None in Blender Source.
        'object_types': {'MESH', 'EMPTY'}, # STOLLIE: Is None in Blender source.
        'use_mesh_modifiers': True,
        'use_mesh_modifiers_render': True,
        'mesh_smooth_type': 'OFF', # STOLLIE: Normally 'FACE' in Blender source.
        'use_subsurf': False,
        'use_armature_deform_only': False,	
        'bake_anim': False, # HARAG: no animation export to SE by default - STOLLIE: True in Blender source.
        'bake_anim_use_all_bones': True,	
        'bake_anim_use_nla_strips': True,	
        'bake_anim_use_all_actions': True,
        'bake_anim_step': 1.0,
        'bake_anim_simplify_factor': 1.0,
        'bake_anim_force_startend_keying': True,
        'add_leaf_bones': False,
        'primary_bone_axis': 'X', # STOLLIE: Swapped for SE, Y in Blender source.	
        'secondary_bone_axis': 'Y', # STOLLIE: Swapped for SE, X in Blender source. """	
        'use_metadata': True,
        'path_mode': 'AUTO',
        'use_mesh_edges': False, # STOLLIE: True in Blender source.
        'use_tspace': False, # BLENDER: Why? Unity is expected to support tspace import...	
        'embed_textures': False,	
        'use_custom_props': False, # HARAG: SE / Havok properties are hacked directly into the modified fbx importer in fbx.py
        # HARAG: The export to Havok needs this, it's off for the MwmFileNode
        # STOLLIE: This is False on Blender source. If set to True on MWM exports it breaks subpart orientations.
        'bake_space_transform': False, 
        'armature_nodetype': 'NULL',	
        'use_selection' : False,
        'use_anim' : False, # HARAG: No animation export to SE by default - STOLLIE: Not a Blender property.
        'use_anim_action_all' : True, # Not a Blender property.	
        'use_default_take' : True, # Not a Blender property.	
        'use_anim_optimize' : True, # Not a Blender property.	
        'anim_optimize_precision' : 6.0, # Not a Blender property.	
        'batch_mode': 'OFF', # STOLLIE: Part of Save method not save single in Blender source, default = OFF.	
        'use_batch_own_dir': True,	# STOLLIE: Part of Save method not save single in Blender source, default = False.	
    }	

    if kwargs:	
        if isinstance(kwargs, bpy.types.PropertyGroup):	
            kwargs = {prop : getattr(kwargs, prop) for prop in kwargs.rna_type.properties.keys()}	
        kwargs.update(**kwargs)	
    
    global_matrix = axis_conversion(to_forward=kwargs['axis_forward'], to_up=kwargs['axis_up']).to_4x4()
    scale = kwargs['global_scale']

    if ishavokfbxfile:
        kwargs['bake_space_transform'] = True
    
    if abs(1.0-scale) >= 0.000001:
        global_matrix = Matrix.Scale(scale, 4) @ global_matrix

    kwargs['global_matrix'] = global_matrix
    
    return save_single(	
        settings.operator,	
        settings.scene,	
        settings.depsgraph,	
        filepath=filepath,	
        **kwargs # Stores any number of Keyword Arguments into a dictionary called 'fbxSettings'.	
    )	