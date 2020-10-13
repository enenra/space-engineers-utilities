import bpy
import os
import re
import math
import glob
import subprocess
import xml.etree.ElementTree as ET
import xml.dom.minidom

from os.path                                import join
from mathutils                              import Matrix	
from bpy_extras.io_utils                    import axis_conversion, ExportHelper

from ..export.seut_custom_fbx_exporter      import save_single
from ..seut_ot_recreate_collections         import get_collections
from ..seut_utils                           import linkSubpartScene, unlinkSubpartScene, getParentCollection, get_preferences

from ..seut_errors                          import report_error, report_warning, get_abs_path

def export_xml(self, context, collection):
    """Exports the XML definition for a collection"""

    scene = context.scene
    collections = get_collections(scene)
    preferences = get_preferences()

    # Create XML tree and add initial parameters.
    model = ET.Element('Model')
    model.set('Name', scene.seut.subtypeId)

    if scene.seut.sceneType != 'character' and scene.seut.sceneType != 'character_animation':
        add_subelement(model, 'RescaleFactor', '1.0')
        add_subelement(model, 'Centered', 'false')
        add_subelement(model, 'RescaleToLengthInMeters', 'false')
            
    elif scene.seut.sceneType == 'character' or scene.seut.sceneType == 'character_animation':
        add_subelement(model, 'RescaleFactor', '0.01')

    if scene.seut.sceneType == 'character' or scene.seut.sceneType == 'character_animation':
        add_subelement(model, 'RotationY', '180')
    
    path = get_abs_path(scene.seut.export_exportPath) + "\\"

    # Write local materials as material entries into XML, write library materials as matrefs into XML
    for mat in bpy.data.materials:

        if mat == None:
            continue
        if mat.users == 0 or mat.users == 1 and mat.use_fake_user:
            continue
        if mat.name[:5] == 'SMAT_':
            continue
        
        elif mat.library == None:
            # If the material is not part of a linked library, I have to account for the possibility that it is a leftover material from import.
            # Those do get cleaned up, but only after the BLEND file is saved, closed and reopened. That may not have happened.
            is_unique = True

            for mtl in bpy.data.materials:
                if mtl.library != None:
                    # There is a material with its name in a linked library but override is turned on.
                    if mtl.name == mat.name and mat.seut.overrideMatLib == True:
                        is_unique = True
                    # There is a material with its name in a linked library and override is turned off.
                    if mtl.name == mat.name and mat.seut.overrideMatLib == False:
                        is_unique = False
                    # There is no material with its name in a linked library.
                    elif mat.library == None and mtl.name == mat.name:
                        is_unique = True
            
            # Material is a local material
            if is_unique:
                mat_entry = ET.SubElement(model, 'Material')
                mat_entry.set('Name', mat.name)

                add_subelement(mat_entry, 'Technique', mat.seut.technique)

                if mat.seut.facing != 'None':
                    add_subelement(mat_entry, 'Facing', mat.seut.facing)
                if mat.seut.windScale != 0:
                    add_subelement(mat_entry, 'WindScale', mat.seut.windScale)
                if mat.seut.windFrequency != 0:
                    add_subelement(mat_entry, 'WindFrequency', mat.seut.windFrequency)
                
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

                if images['cm'] == None and images['ng'] == None and images['add'] == None and images['am'] == None:
                    print("SEUT Info: Local material '%s' does not contain any valid textures. Skipping." % (mat.name))

                else:
                    if not images['cm'] == None:
                        create_texture_entry(mat_entry, mat.name, images, 'cm', 'CM', 'ColorMetalTexture')
                    if not images['ng'] == None:
                        create_texture_entry(mat_entry, mat.name, images, 'ng', 'NG', 'NormalGlossTexture')
                    if not images['add'] == None:
                        create_texture_entry(mat_entry, mat.name, images, 'add', 'ADD', 'AddMapsTexture')
                    if not images['am'] == None:
                        create_texture_entry(mat_entry, mat.name, images, 'am', 'ALPHAMASK', 'AlphamaskTexture')
                    
                    print("SEUT Info: Local material '%s' saved. Don't forget to include relevant DDS texture files in mod!" % (mat.name))
            
            else:
                matRef = ET.SubElement(model, 'MaterialRef')
                matRef.set('Name', mat.name)

        elif mat.library != None:
            matRef = ET.SubElement(model, 'MaterialRef')
            matRef.set('Name', mat.name)
            
    # Write LOD references into the XML, if applicable
    if collection == collections['main']:
        
        lod1Printed = False
        lod2Printed = False

        if collections['lod1'] == None or len(collections['lod1'].objects) == 0:
            print("SEUT Info: Collection 'LOD1' not found or empty. Skipping XML entry.")
        else:
            create_lod_entry(scene, model, scene.seut.export_lod1Distance, path, '_LOD1')
            lod1Printed = True

        if collections['lod2'] == None or len(collections['lod2'].objects) == 0:
            print("SEUT Info: Collection 'LOD2' not found or empty. Skipping XML entry.")
        else:
            if lod1Printed:
                create_lod_entry(scene, model, scene.seut.export_lod2Distance, path, '_LOD2')
                lod2Printed = True
            else:
                report_error(self, context, True, 'E006')

        if collections['lod3'] == None or len(collections['lod3'].objects) == 0:
            print("SEUT Info: Collection 'LOD3' not found or empty. Skipping XML entry.")
        else:
            if lod2Printed:
                create_lod_entry(scene, model, scene.seut.export_lod3Distance, path, '_LOD3')
            else:
                report_error(self, context, True, 'E006')

    if collection == collections['bs1'] or collection == collections['bs2'] or collection == collections['bs3']:
        if collections['bs_lod'] == None or len(collections['bs_lod'].objects) == 0:
            print("SEUT Info: Collection 'BS_LOD' not found or empty. Skipping XML entry.")
        else:
            create_lod_entry(scene, model, scene.seut.export_bs_lodDistance, path, '_BS_LOD')

    # Create file with subtypename + collection name and write string to it
    temp_string = ET.tostring(model, 'utf-8')
    try:
        temp_string.decode('ascii')
    except UnicodeDecodeError:
        report_error(self, context, False, 'E033')
    xml_string = xml.dom.minidom.parseString(temp_string)
    xml_formatted = xml_string.toprettyxml()
    
    filetype = collection.name[:collection.name.find(" (")]
    
    if collection == collections['main']:
        filename = scene.seut.subtypeId
    else:
        filename = scene.seut.subtypeId + '_' + filetype

    exported_xml = open(path + filename + ".xml", "w")
    exported_xml.write(xml_formatted)
    print("SEUT Info: '%s.xml' has been created." % (path + filename))


def add_subelement(parent, name: str, value):
    """Adds a subelement to XML definition"""
    
    param = ET.SubElement(parent, 'Parameter')
    param.set('Name', name)
    param.text = str(value)


def create_texture_entry(mat_entry, mat_name: str, images: dict, tex_type: str, tex_name: str, tex_name_long: str, ):
    """Creates a texture entry for a texture type into the XML tree"""
    
    offset = 0
    offset = images[tex_type].filepath.find("Textures\\")
    
    if offset == -1:
        report_error(self, context, True, 'E007', tex_name, mat_name)
    else:
        add_subelement(mat_entry, tex_name_long, os.path.splitext(images[tex_type].filepath[offset:])[0] + ".dds")
    
    if not is_valid_resolution(images[tex_type].size[0]) or not is_valid_resolution(images[tex_type].size[1]):
        report_warning(self, context, True, 'W004', tex_name, mat_name, str(images[tex_type].size[0]) + "x" + str(images[tex_type].size[1]))


def is_valid_resolution(number: int) -> bool:
    """Returns True if number is a valid resolution (a square of 2)"""
    
    if number <= 0:
        return False

    return math.log(number, 2).is_integer()


def create_lod_entry(scene, tree, distance: int, path: str, lod_type: str):
    """Creates a LOD entry into the XML tree"""
    
    lod = ET.SubElement(tree, 'LOD')
    lod.set('Distance', str(distance))
    lodModel = ET.SubElement(lod, 'Model')
    lodModel.text = path[path.find("Models\\"):] + scene.seut.subtypeId + lod_type


def export_model_FBX(self, context, collection):
    """Exports the FBX file for a defined collection"""

    scene = context.scene
    depsgraph = context.evaluated_depsgraph_get()
    addon = __package__[:__package__.find(".")]
    preferences = bpy.context.preferences.addons.get(addon).preferences
    collections = get_collections(scene)
    settings = ExportSettings(scene, depsgraph)

    # Determining the directory to export to.
    filetype = collection.name[:collection.name.find(" (")]

    if collection == collections['main']:
        filename = scene.seut.subtypeId
    else:
        filename = scene.seut.subtypeId + '_' + filetype

    path = os.path.abspath(bpy.path.abspath(scene.seut.export_exportPath)) + "\\"
    
    # Exporting the collection.
    # I can only export the currently active collection, so I need to set the target collection to active (for which I have to link it for some reason),
    # then export, then unlink. User won't see it and it shouldn't make a difference.
    try:
        bpy.context.scene.collection.children.link(collection)
    except:
        pass
    layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]
    bpy.context.view_layer.active_layer_collection = layer_collection
    
    # Unlink all subparts parented to an empty
    for emptyObj in collection.objects:
        if emptyObj is not None and emptyObj.type == 'EMPTY':
            
            # To ensure they work ingame (where duplicate names are no issue) this will remove the ".001" etc. from the name (and cause another empty to get this numbering)
            if re.search("\.[0-9]{3}", emptyObj.name[-4:]) != None and emptyObj.name.find("(L)") == -1:
                emptyObj.name = emptyObj.name[:-4]
                # For some godforsaken reason, sometimes the name just isn't shortened. But trying it again seems to do the trick...
                if re.search("\.[0-9]{3}", emptyObj.name[-4:]) != None:
                    emptyObj.name = emptyObj.name[:-4]

            if emptyObj.parent is None:
                print("SEUT Warning: Empty '" + emptyObj.name + "' has no parent object. This may prevent it from working properly ingame.")
            elif emptyObj.parent.parent is not None:
                print("SEUT Warning: Parent of empty '" + emptyObj.name + "' ('" + emptyObj.parent.name + "') has a parent object. This may prevent the empty from working properly ingame.")

            if 'highlight' in emptyObj and emptyObj.seut.linkedObject is not None:
                emptyObj['highlight'] = emptyObj.seut.linkedObject.name
                if emptyObj.parent is not None and emptyObj.seut.linkedObject.parent is not None and emptyObj.parent != emptyObj.seut.linkedObject.parent:
                    print("SEUT Warning: Highlight empty '" + emptyObj.name + "' and its linked object '" + emptyObj.seut.linkedObject.name + "' have different parent objects. This may prevent it from working properly ingame.")
            elif 'file' in emptyObj and emptyObj.seut.linkedScene is not None:

                parentCollection = getParentCollection(context, emptyObj)
                
                collectionType = 'main'
                extension = ""
                if parentCollection == collections['bs1']:
                    collectionType = 'bs1'
                    extension = "_BS1"
                elif parentCollection == collections['bs2']:
                    collectionType = 'bs2'
                    extension = "_BS2"
                elif parentCollection == collections['bs3']:
                    collectionType = 'bs3'
                    extension = "_BS3"

                reference = emptyObj.seut.linkedScene.seut.subtypeId + extension

                # Account for simultaneous export
                if scene.seut.export_largeGrid and scene.seut.export_smallGrid:
                    if scene.seut.subtypeId.find("LG_") != None:
                        if reference.find("LG_") != None:
                            pass
                        elif reference.find("SG_") != None:
                            reference = reference.replace("SG_", "LG_")
                        else:
                            reference = "LG_" + reference

                    elif scene.seut.subtypeId.find("SG_") != None:
                        if reference.find("SG_") != None:
                            pass
                        elif reference.find("LG_") != None:
                            reference = reference.replace("LG_", "SG_")
                        else:
                            reference = "SG_" + reference
                    
                emptyObj['file'] = reference
                unlinkSubpartScene(emptyObj)
            
            # Blender FBX export halves empty size on export, this works around it
            if 'MaxHandle' not in emptyObj and 'file' not in emptyObj:
                emptyObj.scale.x *= 2
                emptyObj.scale.y *= 2
                emptyObj.scale.z *= 2

    for objMat in bpy.data.materials:
        if objMat is not None and objMat.node_tree is not None:
            prepMatForExport(self, context, objMat)

    # This is the actual call to make an FBX file.
    fbxfile = join(path, filename + ".fbx")
    errorDuringExport = False
    try:
        export_to_fbxfile(settings, scene, fbxfile, collection.objects, ishavokfbxfile=False)
    except RuntimeError as error:
        report_error(self, context, False, 'E036')
        errorDuringExport = True

    for objMat in bpy.data.materials:
        if objMat is not None and objMat.node_tree is not None:
            removeExportDummiesFromMat(self, context, objMat)
    
    # Relink all subparts to empties
    for emptyObj in collection.objects:
        if emptyObj is not None and emptyObj.type == 'EMPTY':
            
            if scene.seut.linkSubpartInstances:
                if 'file' in emptyObj and emptyObj.seut.linkedScene is not None and emptyObj.seut.linkedScene.name in bpy.data.scenes:
                    parentCollection = getParentCollection(context, emptyObj)

                    collectionType = 'main'
                    extension = ""
                    if parentCollection == collections['bs1']:
                        collectionType = 'bs1'
                        extension = "_BS1"
                    elif parentCollection == collections['bs2']:
                        collectionType = 'bs2'
                        extension = "_BS2"
                    elif parentCollection == collections['bs3']:
                        collectionType = 'bs3'
                        extension = "_BS3"
                        
                    linkSubpartScene(self, scene, emptyObj, parentCollection, collectionType)
                    emptyObj['file'] = emptyObj.seut.linkedScene.seut.subtypeId + extension

            # Resetting empty size
            if 'MaxHandle' not in emptyObj and 'file' not in emptyObj:
                emptyObj.scale.x *= 0.5
                emptyObj.scale.y *= 0.5
                emptyObj.scale.z *= 0.5

    bpy.context.scene.collection.children.unlink(collection)
    if not errorDuringExport:
        print("SEUT Info: '%s.fbx' has been created." % (path + filename))

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
        try:
            material.seut.nodeLinkedToOutputName = materialOutput.inputs[0].links[0].from_node.name
        except IndexError:
            print("SEUT Info: IndexError at material '" + material.name + "'.")

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
        try:
            material.node_tree.links.new(nodeLinkedToOutput.outputs[0], materialOutput.inputs[0])
        except IndexError:
            print("SEUT Info: IndexError at material '" + material.name + "'.")

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

    toolPath = os.path.abspath(bpy.path.abspath(toolPath))
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
        report_error(self, context, False, 'E020')

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

    def callTool(self, context, cmdline, tooltype, logfile=None, cwd=None, successfulExitCodes=[0], loglines=[], logtextInspector=None):
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
                report_error(self, context, False, 'E035', str(tooltype))
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
        
        # Operator settings
        'version': 'BIN7400',
        'path_mode': 'AUTO',
        'batch_mode': 'OFF', # STOLLIE: Part of Save method not save single in Blender source, default = OFF.	

        # Include settings.
        'object_types': {'MESH', 'EMPTY'}, # STOLLIE: Is None in Blender source.
        'use_custom_props': False, # HARAG: SE / Havok properties are hacked directly into the modified fbx importer in fbx.py

        # Transform settings.
        'global_scale': 0.1, # STOLLIE: Is 1.0 in Blender Source
        'apply_scale_options': 'FBX_SCALE_NONE',        
        'axis_forward': 'Z', # STOLLIE: Normally a Y in Blender source. -Z is correct forward.
        'axis_up': 'Y',	 # STOLLIE: Normally a Z in Blender source.	Y aligns correctly in SE.
        
        # HARAG: The export to Havok needs this, it's off for the MwmFileNode (bake_space_transform).
        # STOLLIE: This is False on Blender source. If set to True on MWM exports it breaks subpart orientations (bake_space_transform).
        'bake_space_transform': False,

        # Geometry settings.
        'mesh_smooth_type': 'OFF', # STOLLIE: Normally 'FACE' in Blender source.
        'use_subsurf': False,
        'use_mesh_modifiers': True,
        'use_mesh_edges': False, # STOLLIE: True in Blender source.
        'use_tspace': False, # BLENDER: Why? Unity is expected to support tspace import...	
        'use_mesh_modifiers_render': True,

         # For amature.
        'primary_bone_axis': 'X', # STOLLIE: Swapped for SE, Y in Blender source.	
        'secondary_bone_axis': 'Y', # STOLLIE: Swapped for SE, X in Blender source.
        'armature_nodetype': 'NULL',
        'use_armature_deform_only': False,
        'add_leaf_bones': False,

        # For animations.
        'bake_anim': False, # HARAG: no animation export to SE by default - STOLLIE: True in Blender source.
        'bake_anim_use_all_bones': True,
        'bake_anim_use_nla_strips': True,
        'bake_anim_use_all_actions': True,
        'bake_anim_force_startend_keying': True,
        'bake_anim_step': 1.0,
        'bake_anim_simplify_factor': 1.0,
                
        # Random properties not seen in Blender FBX export UI.
        'ui_tab': 'SKIP_SAVE',
        'global_matrix': Matrix(),
        'use_metadata': True,
        'embed_textures': False,
        'use_anim' : False, # HARAG: No animation export to SE by default - STOLLIE: Not a Blender property.
        'use_anim_action_all' : True, # Not a Blender property.	
        'use_default_take' : True, # Not a Blender property.	
        'use_anim_optimize' : True, # Not a Blender property.	
        'anim_optimize_precision' : 6.0, # Not a Blender property.	
        'use_batch_own_dir': True,	# STOLLIE: Part of Save method not save single in Blender source, default = False.
    }	

    if kwargs:	
        if isinstance(kwargs, bpy.types.PropertyGroup):	
            kwargs = {prop : getattr(kwargs, prop) for prop in kwargs.rna_type.properties.keys()}	
        kwargs.update(**kwargs)

    # These cannot be overriden and are always set here
    kwargs['use_selection'] = False # because of context_objects
    kwargs['context_objects'] = objects	# STOLLIE: Is None in Blender Source.

    if ishavokfbxfile:
        kwargs['bake_space_transform'] = True        
    
    if scene.seut.sceneType == 'subpart':
        kwargs['axis_forward'] = '-Z'

    if scene.seut.sceneType == 'character':
        kwargs['global_scale'] = 1.00
        kwargs['axis_forward'] = '-Z'
        kwargs['object_types'] = {'MESH', 'EMPTY', 'ARMATURE'} # STOLLIE: Is None in Blender source.
        kwargs['add_leaf_bones'] = True # HARAG: No animation export to SE by default - STOLLIE: Not a Blender property.     
        kwargs['apply_unit_scale'] = True # HARAG: No animation export to SE by default - STOLLIE: Not a Blender property.    

    if scene.seut.sceneType == 'character_animation':
        kwargs['axis_forward'] = '-Z'
        kwargs['object_types'] = {'EMPTY', 'ARMATURE'} # STOLLIE: Is None in Blender source.
        kwargs['use_armature_deform_only'] = True
        kwargs['bake_anim'] = True # HARAG: no animation export to SE by default - STOLLIE: True in Blender source.
        kwargs['bake_anim_simplify_factor'] = 0.0
        kwargs['use_anim'] = True # HARAG: No animation export to SE by default - STOLLIE: Not a Blender property.
        kwargs['apply_unit_scale'] = True # HARAG: No animation export to SE by default - STOLLIE: Not a Blender property.    

    # if scene.seut.sceneType != 'character' and scene.seut.sceneType != 'character_animation':
    global_matrix = axis_conversion(to_forward=kwargs['axis_forward'], to_up=kwargs['axis_up']).to_4x4()
    scale = kwargs['global_scale']

    scale *= scene.seut.export_rescaleFactor

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