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
from ..materials.seut_materials             import dlc_materials
from ..seut_collections                     import get_collections, names
from ..seut_utils                           import link_subpart_scene, unlink_subpart_scene, get_parent_collection, get_preferences
from ..seut_errors                          import seut_report, get_abs_path

def export_xml(self, context, collection) -> str:
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
        # This is a legacy check to filter out the old material presets.
        if mat.name[:5] == 'SMAT_':
            continue

        if mat.name in dlc_materials:
            seut_report(self, context, 'WARNING', False, 'W012', mat.name)
        
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
                create_mat_entry(self, context, model, mat)
            
            else:
                matRef = ET.SubElement(model, 'MaterialRef')
                matRef.set('Name', mat.name)

        elif mat.library != None:
            matRef = ET.SubElement(model, 'MaterialRef')
            matRef.set('Name', mat.name)
            
    # Write LOD references into the XML, if applicable
    if collection.seut.col_type == 'main':

        printed = {}
        if not collections['lod'] is None:
            for key, value in collections['lod'].items():
                lod_col = value
                if len(lod_col.objects) == 0:
                    seut_report(self, context, 'INFO', False, 'I003', 'LOD' + str(lod_col.seut.type_index))
                else:
                    if key == 1 or key - 1 in printed and printed[key - 1]:
                        create_lod_entry(scene, model, lod_col.seut.lod_distance, path, '_LOD' + str(lod_col.seut.type_index))
                        printed[key] = True
                    else:
                        seut_report(self, context, 'ERROR', True, 'E006')
    
    elif collection.seut.col_type == 'bs':

        printed = {}
        if not collections['bs_lod'] is None:
            for key, value in collections['bs_lod'].items():
                lod_col = value
                if len(lod_col.objects) == 0:
                    seut_report(self, context, 'INFO', False, 'I003', 'BS_LOD' + str(lod_col.seut.type_index))
                else:
                    if key == 1 or key - 1 in printed and printed[key - 1]:
                        create_lod_entry(scene, model, lod_col.seut.lod_distance, path, '_BS_LOD' + str(lod_col.seut.type_index))
                        printed[key] = True
                    else:
                        seut_report(self, context, 'ERROR', True, 'E006')
        
    # Create file with subtypename + collection name and write string to it
    xml_formatted = format_xml(self, context, model)
    
    filetype = collection.name[:collection.name.find(" (")]
    
    if collection == collections['main']:
        filename = scene.seut.subtypeId
    else:
        filename = scene.seut.subtypeId + '_' + filetype

    exported_xml = open(path + filename + ".xml", "w")
    exported_xml.write(xml_formatted)
    seut_report(self, context, 'INFO', True, 'I004', path + filename + ".xml")

    return {'FINISHED'}


def add_subelement(parent, name: str, value):
    """Adds a subelement to XML definition"""
    
    param = ET.SubElement(parent, 'Parameter')
    param.set('Name', name)
    param.text = str(value)


def create_texture_entry(self, context, mat_entry, mat_name: str, images: dict, tex_type: str, tex_name: str, tex_name_long: str, ):
    """Creates a texture entry for a texture type into the XML tree"""
    
    rel_path = create_relative_path(images[tex_type].filepath, "Textures")
    
    if not rel_path:
        seut_report(self, context, 'ERROR', True, 'E007', tex_name, mat_name)
    else:
        add_subelement(mat_entry, tex_name_long, os.path.splitext(rel_path)[0] + ".dds")
    
    if not is_valid_resolution(images[tex_type].size[0]) or not is_valid_resolution(images[tex_type].size[1]):
        seut_report(self, context, 'WARNING', True, 'W004', tex_name, mat_name, str(images[tex_type].size[0]) + "x" + str(images[tex_type].size[1]))


def create_relative_path(path: str, foldername: str):
    """Returns the path capped off before the last occurrence of the foldername, returns False if foldername is not found in path"""
    
    offset = path.rfind(foldername + "\\")

    if offset == -1:
        return False
    else:
        return path[path.rfind(foldername + "\\"):]


def is_valid_resolution(number: int) -> bool:
    """Returns True if number is a valid resolution (a square of 2)"""
    
    if number <= 0:
        return False

    return math.log(number, 2).is_integer()


def create_mat_entry(self, context, tree, mat):
    """Creates a material entry in the given tree for a given material"""

    mat_entry = ET.SubElement(tree, 'Material')
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
        tree.remove(mat_entry)
        seut_report(self, context, 'INFO', False, 'I001', mat.name)

    else:
        if not images['cm'] == None:
            create_texture_entry(self, context, mat_entry, mat.name, images, 'cm', 'CM', 'ColorMetalTexture')
        if not images['ng'] == None:
            create_texture_entry(self, context, mat_entry, mat.name, images, 'ng', 'NG', 'NormalGlossTexture')
        if not images['add'] == None:
            create_texture_entry(self, context, mat_entry, mat.name, images, 'add', 'ADD', 'AddMapsTexture')
        if not images['am'] == None:
            create_texture_entry(self, context, mat_entry, mat.name, images, 'am', 'ALPHAMASK', 'AlphamaskTexture')
        
        seut_report(self, context, 'INFO', False, 'I002', mat.name)


def create_lod_entry(scene, tree, distance: int, path: str, lod_type: str):
    """Creates a LOD entry into the XML tree"""
    
    lod = ET.SubElement(tree, 'LOD')
    lod.set('Distance', str(distance))
    lodModel = ET.SubElement(lod, 'Model')
    lodModel.text = create_relative_path(path, "Models") + scene.seut.subtypeId + lod_type


def format_xml(self, context, tree) -> str:
    """Converts XML Tree to a formatted XML string"""

    temp_string = ET.tostring(tree, 'utf-8')

    try:
        temp_string.decode('ascii')

    except UnicodeDecodeError:
        seut_report(self, context, 'ERROR', False, 'E033')

    xml_string = xml.dom.minidom.parseString(temp_string)
    
    return xml_string.toprettyxml()


def export_fbx(self, context, collection) -> str:
    """Exports the FBX file for a defined collection"""

    scene = context.scene
    preferences = get_preferences()
    collections = get_collections(scene)
    depsgraph = context.evaluated_depsgraph_get()
    settings = ExportSettings(scene, depsgraph)

    path = get_abs_path(scene.seut.export_exportPath) + "\\"
    
    # Export exports the active layer_collection so the collection's layer_collection needs to be set as the active one
    try:
        bpy.context.scene.collection.children.link(collection)
    except:
        pass
    layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]
    bpy.context.view_layer.active_layer_collection = layer_collection
    
    # Prepare empties for export
    for empty in collection.objects:
        if empty is not None and empty.type == 'EMPTY':
            
            # Remove numbers
            # To ensure they work ingame (where duplicate names are no issue) this will remove the ".001" etc. from the name (and cause another empty to get this numbering)
            if re.search("\.[0-9]{3}", empty.name[-4:]) != None and empty.name.find("(L)") == -1:
                if empty.name[:-4] in bpy.data.objects:
                    temp_obj = bpy.data.objects[empty.name[:-4]]
                    temp_obj.name = empty.name + " TEMP"
                    empty.name = empty.name[:-4]
                    temp_obj.name = temp_obj.name[:-len(" TEMP")]
                else:
                    empty.name = empty.name[:-4]

            # Check parenting
            if empty.parent is None:
                seut_report(self, context, 'WARNING', True, 'W005', empty.name, collection.name)
            elif empty.parent.parent is not None:
                seut_report(self, context, 'WARNING', True, 'W006', empty.name, empty.parent.name, collection.name)

            # Additional parenting checks
            rescale = False
            if 'highlight' in empty and len(empty.seut.highlight_objects) > 0:

                highlights = ""
                for entry in empty.seut.highlight_objects:
                    if not empty is None and not entry.obj is None:
                        if empty.parent is not None and entry.obj.parent is not None and empty.parent != entry.obj.parent:
                            seut_report(self, context, 'WARNING', True, 'W007', empty.name, entry.obj.name)

                        if highlights == "":
                            highlights = entry.obj.name
                        else:
                            highlights = highlights + ';' + entry.obj.name

                empty['highlight'] = highlights

                rescale = True
            
            elif 'file' in empty and empty.seut.linkedScene is not None:
                linked_scene = empty.seut.linkedScene
                if linked_scene.seut.export_largeGrid != scene.seut.export_largeGrid or linked_scene.seut.export_smallGrid != scene.seut.export_smallGrid:
                    seut_report(self, context, 'WARNING', True, 'W013', linked_scene.name, scene.name)

                # Remove subpart instances
                reference = get_subpart_reference(empty, collections)
                reference = correct_for_export_type(scene, reference)
                empty['file'] = reference
                unlink_subpart_scene(empty)

                rescale = True
            
            # Blender FBX export halves empty size on export, this works around it
            if rescale:
                empty.scale.x *= 2
                empty.scale.y *= 2
                empty.scale.z *= 2
                context.view_layer.update()

    # Prepare materials for export
    for mat in bpy.data.materials:
        if mat is not None and mat.node_tree is not None:
            prepare_mat_for_export(self, context, mat)

    # Export the collection to FBX
    filetype = collection.name[:collection.name.find(" (")]
    if collection == collections['main']:
        filename = scene.seut.subtypeId
    else:
        filename = scene.seut.subtypeId + '_' + filetype

    fbx_file = join(path, filename + ".fbx")
    error_during_export = False
    try:
        export_to_fbxfile(settings, scene, fbx_file, collection.objects, ishavokfbxfile=False)

    except RuntimeError as error:
        seut_report(self, context, 'ERROR', False, 'E017')
        error_during_export = True

    except KeyError as error:
        seut_report(self, context, 'ERROR', True, 'E038', error)

    # Revert materials back to original form
    for mat in bpy.data.materials:
        if mat is not None and mat.node_tree is not None:
            revert_mat_after_export(self, context, mat)
    
    # Relink all subparts to empties
    for empty in collection.objects:
        if empty is not None and empty.type == 'EMPTY':
            
            if scene.seut.linkSubpartInstances:
                if 'file' in empty and empty.seut.linkedScene is not None and empty.seut.linkedScene.name in bpy.data.scenes:                    
                    reference = get_subpart_reference(empty, collections)
                        
                    link_subpart_scene(self, scene, empty, empty.users_collection[0])
                    empty['file'] = reference

            # Resetting empty size
            if 'file' in empty or 'highlight' in empty :
                empty.scale.x *= 0.5
                empty.scale.y *= 0.5
                empty.scale.z *= 0.5

    bpy.context.scene.collection.children.unlink(collection)

    if not error_during_export:
        seut_report(self, context, 'INFO', True, 'I004', path + filename + ".fbx")
        return {'CANCELLED'}

    return {'FINISHED'}


def get_subpart_reference(empty, collections: dict) -> str:
    """Returns the corrected subpart reference."""

    parent_collection = empty.users_collection[0]

    if parent_collection.seut.col_type == 'bs':
        for bs in collections['bs'].values():
            if parent_collection == bs:
                return empty.seut.linkedScene.seut.subtypeId + "_" + names['bs'] + str(bs.seut.type_index)

    return empty.seut.linkedScene.seut.subtypeId


def correct_for_export_type(scene, reference: str) -> str:
    """Corrects reference depending on export type (large / small) selected."""

    if scene.seut.gridScale == 'large':
        if reference.startswith("LG_") or reference.find("_LG_") != -1 or reference.endswith("_LG"):
            pass

        elif reference.startswith("SG_") or reference.find("_SG_") != -1 or reference.endswith("_SG"):
            if reference.startswith("SG_"):
                reference = reference.replace("SG_", "LG_")
            elif reference.find("_SG_") != -1:
                reference = reference.replace("_SG_", "_LG_")
            elif reference.endswith("_SG"):
                reference = reference.replace("_SG", "_LG")

        elif scene.seut.export_largeGrid and scene.seut.export_smallGrid:
            reference = "LG_" + reference

    elif scene.seut.gridScale == 'small':
        if reference.startswith("SG_") or reference.find("_SG_") != -1 or reference.endswith("_SG"):
            pass

        elif reference.startswith("LG_") or reference.find("_LG_") != -1 or reference.endswith("_LG"):
            if reference.startswith("LG_"):
                reference = reference.replace("LG_", "SG_")
            elif reference.find("_LG_") != -1:
                reference = reference.replace("_LG_", "_SG_")
            elif reference.endswith("_LG"):
                reference = reference.replace("_LG", "_SG")

        elif scene.seut.export_largeGrid and scene.seut.export_smallGrid:
            reference = "SG_" + reference

    return reference


def prepare_mat_for_export(self, context, material):
    """Switches material around so that SE can properly read it"""
    
    # See if relevant nodes already exist
    dummy_shader_node = None
    dummy_image_node = None
    dummy_image = None
    material_output = None

    for node in material.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED' and node.name == 'EXPORT_DUMMY':
            dummy_shader_node = node
        elif node.type == 'TEX_IMAGE' and node.name == 'DUMMY_IMAGE':
            dummy_image_node = node
        elif node.type == 'OUTPUT_MATERIAL':
            material_output = node

    # Iterate through images to find the dummy image
    for img in bpy.data.images:
        if img.name == 'DUMMY':
            dummy_image = img

    # If it doesn't exist, create it and a DUMMY image node, and link them up
    if dummy_image_node is None:
        dummy_image_node = material.node_tree.nodes.new('ShaderNodeTexImage')
        dummy_image_node.name = 'DUMMY_IMAGE'
        dummy_image_node.label = 'DUMMY_IMAGE'

    if dummy_image is None:
        dummy_image = bpy.data.images.new('DUMMY', 1, 1)

    if dummy_shader_node is None:
        dummy_shader_node = material.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
        dummy_shader_node.name = 'EXPORT_DUMMY'
        dummy_shader_node.label = 'EXPORT_DUMMY'
    
    if material_output is None:
        material_output = material.node_tree.nodes.new('ShaderNodeOutputMaterial')
        material.seut.nodeLinkedToOutputName = ""

    # This allows the reestablishment of connections after the export is complete.
    else:
        try:
            material.seut.nodeLinkedToOutputName = material_output.inputs[0].links[0].from_node.name
        except IndexError:
            seut_report(self, context, 'INFO', False, 'I005', material.name)

    # link nodes, add image to node
    material.node_tree.links.new(dummy_image_node.outputs[0], dummy_shader_node.inputs[0])
    material.node_tree.links.new(dummy_shader_node.outputs[0], material_output.inputs[0])
    dummy_image_node.image = dummy_image


def revert_mat_after_export(self, context, material):
    """Removes the dummy nodes from the material again after export"""

    material_output = None
    node_linked_to_output = None

    # Remove dummy nodes - do I need to remove the links too?
    # Image can stay, it's 1x1 px so nbd
    for node in material.node_tree.nodes:
        if node.type == 'TEX_IMAGE' and node.name == 'DUMMY_IMAGE':
            material.node_tree.nodes.remove(node)
        elif node.type == 'BSDF_PRINCIPLED' and node.name == 'EXPORT_DUMMY':
            material.node_tree.nodes.remove(node)
        elif node.type == 'OUTPUT_MATERIAL':
            material_output = node
        elif node.name == material.seut.nodeLinkedToOutputName:
            node_linked_to_output = node
    
    # link the node group back to output
    if node_linked_to_output is not None:
        try:
            material.node_tree.links.new(node_linked_to_output.outputs[0], material_output.inputs[0])
        except IndexError:
            seut_report(self, context, 'INFO', False, 'I005', material.name)


def export_collection(self, context, collection):
    """Exports the collection to XML and FBX"""

    print("\n------------------------------ Exporting Collection '" + collection.name + "'.")
    result_xml = export_xml(self, context, collection)
    result_fbx = export_fbx(self, context, collection)
    print("------------------------------ Finished exporting Collection '" + collection.name + "'.\n")

    return result_xml, result_fbx


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

def delete_loose_files(self, context, path):
    fileRemovalList = [fileName for fileName in glob.glob(path + "*.*") if "fbx" in fileName or
        "xml" in fileName or "hkt" in fileName or "log" in fileName]

    try:
        for fileName in fileRemovalList:
            os.remove(fileName)

    except EnvironmentError:
        seut_report(self, context, 'ERROR', False, 'E020')

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
            self._fbximporter = tool_path('fbx_importer_path', 'Custom FBX Importer')
        return self._fbximporter

    @property
    def havokfilter(self):
        if self._havokfilter == None:
            self._havokfilter = tool_path('havok_path', 'Havok Standalone Filter Tool')
        return self._havokfilter

    @property
    def mwmbuilder(self):
        if self._mwmbuilder == None:
            self._mwmbuilder = tool_path('mwmb_path', 'MWM Builder')
        return self._mwmbuilder

    def callTool(self, context, cmdline, tooltype, logfile=None, cwd=None, successfulExitCodes=[0], loglines=[], logtextInspector=None):
        try:
            out = subprocess.check_output(cmdline, cwd=cwd, stderr=subprocess.STDOUT, shell=True)
            if self.isLogToolOutput and logfile:
                write_to_log(logfile, out, cmdline=cmdline, cwd=cwd, loglines=loglines)
            if logtextInspector is not None:
                logtextInspector(out)

            out_str = out.decode("utf-8")
            if out_str.find(": ERROR:") != -1:
                if out_str.find("Assimp.AssimpException: Error loading unmanaged library from path: Assimp32.dll") != -1:
                    seut_report(self, context, 'ERROR', False, 'E039')
                    return False
                    
                elif out_str.find("System.ArgumentOutOfRangeException: Index was out of range. Must be non-negative and less than the size of the collection.") != -1:
                    temp_string = out_str[out_str.find("\\Models\\") + len("\\Models\\"):]
                    temp_string = temp_string[:temp_string.find(".fbx")]
                    seut_report(self, context, 'ERROR', False, 'E043', temp_string + ".fbx")
                    return False
            
                else:
                    seut_report(self, context, 'ERROR', False, 'E044')
                    return False

            return True

        except subprocess.CalledProcessError as e:
            if self.isLogToolOutput and logfile:
                write_to_log(logfile, e.output, cmdline=cmdline, cwd=cwd, loglines=loglines)
            if e.returncode not in successfulExitCodes:
                if e.returncode == 4294967295:
                    seut_report(self, context, 'ERROR', False, 'E037')
                else:
                    seut_report(self, context, 'ERROR', False, 'E035', str(tooltype))
                raise

            return False
    
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