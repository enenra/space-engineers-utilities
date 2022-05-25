import bpy

from bpy.types              import Operator
from bpy.props              import (EnumProperty,
                                    FloatProperty,
                                    FloatVectorProperty,
                                    IntProperty,
                                    StringProperty,
                                    BoolProperty,
                                    PointerProperty,
                                    CollectionProperty
                                    )
from bpy_extras.io_utils    import ImportHelper

from ..seut_preferences import get_preferences
from ..seut_collections import get_collections
from ..seut_errors      import get_abs_path, seut_report
from .seut_planet_io    import *
from .seut_planet_utils import *


class SEUT_OT_Planet_RecreateSetup(Operator):
    """(Re)-spawns the planet editor object setup"""
    bl_idname = "planet.recreate_setup"
    bl_label = "Spawn Setup"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene

        if scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers:
            if scene.seut.bake_target is not None and scene.seut.bake_source is not None:
                Operator.poll_message_set("All objects are present.")
                return False
        return True


    def execute(self, context):
        scene = context.scene
        preferences = get_preferences()
        collections = get_collections(scene)

        if preferences.asset_path == "":
            seut_report(self, context, 'ERROR', True, 'E012', "Asset Directory", get_abs_path(preferences.asset_path))
            return {'CANCELLED'}

        file_path = os.path.join(get_abs_path(preferences.asset_path), 'Models', 'planet_editor.blend')
        if not os.path.exists(file_path):
            print("Could not find shit, chief.") # TODO: seut_report replacement
            return {'CANCELLED'}
        
        if not 'main' in collections or collections['main'] == [] or collections['main'][0] is None:
            print("Could not find shit, chief.") # TODO: seut_report replacement
            return {'CANCELLED'}
        
        context.view_layer.active_layer_collection = scene.view_layers['SEUT'].layer_collection.children[collections['seut'][0].name].children[collections['main'][0].name]

        def append_object(context: bpy.context, file_path: os.path, name: str) -> object:
            existing_objects = set(context.scene.objects)
            bpy.ops.wm.append(
                filepath=os.path.join(file_path, 'Object', name),
                directory=os.path.join(file_path, 'Object'),
                filename=name
            )
            new_objects = set(context.scene.objects)
            imported_objects = new_objects.copy()

            for new in new_objects:
                for existing in existing_objects:
                    if new == existing:
                        imported_objects.remove(new)
            
            if len(imported_objects) < 1:
                return -1

            return next(iter(imported_objects))

        if scene.seut.bake_target is None:
            appended_obj = append_object(context, file_path, 'BAKE TARGET')
            if appended_obj == -1:
                seut_report(self, context, 'ERROR', True, 'E049')
                return {'CANCELLED'}
            else:
                scene.seut.bake_target = appended_obj
        if scene.seut.bake_source is None:
            appended_obj = append_object(context, file_path, 'BAKE SOURCE')
            if appended_obj == -1:
                seut_report(self, context, 'ERROR', True, 'E049')
                return {'CANCELLED'}
            else:
                scene.seut.bake_source = appended_obj
        
        mats = ['front', 'back', 'right', 'left', 'top', 'bottom', 'SURFACE']
        for mat in bpy.data.materials:
            if mat.name in mats:
                mat.use_fake_user = True
        
        return {'FINISHED'}


class SEUT_OT_Planet_MaterialGroup_Add(Operator):
    """Adds a Material Group to a Planet"""
    bl_idname = "planet.add_material_group"
    bl_label = "Add Material Group"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        
        add_material_group(context)

        return {'FINISHED'}


class SEUT_OT_Planet_MaterialGroup_Remove(Operator):
    """Removes a Material Group from a Planet"""
    bl_idname = "planet.remove_material_group"
    bl_label = "Remove Material Group"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        scene = context.scene

        scene.seut.material_groups.remove(scene.seut.material_groups_index)
        
        for c in scene.seut.material_groups_palette.colors:
            found = False
            for mg in scene.seut.material_groups:
                if mg.value == int(round(c.color[0] * 255)) and c.color[1] == 0 and c.color[2] == 0:
                    found = True
            if not found:
                scene.seut.material_groups_palette.colors.remove(c)


        return {'FINISHED'}


class SEUT_OT_Planet_DistributionRule_Add(Operator):
    """Adds a Distribution Rule"""
    bl_idname = "planet.add_distribution_rule"
    bl_label = "Add Distribution Rule"
    bl_options = {'REGISTER', 'UNDO'}


    rule_type: StringProperty(
        default='material_group'
    )


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        scene = context.scene

        if self.rule_type == 'material_group':
            rule_type = scene.seut.material_groups[scene.seut.material_groups_index]
        elif self.rule_type == 'environment_item':
            rule_type = scene.seut.environment_items[scene.seut.environment_items_index]

        item = rule_type.rules.add()
        item.name = "Rule " + str(len(rule_type.rules))

        return {'FINISHED'}


class SEUT_OT_Planet_DistributionRule_Remove(Operator):
    """Removes a Distribution Rule"""
    bl_idname = "planet.remove_distribution_rule"
    bl_label = "Remove Distribution Rule"
    bl_options = {'REGISTER', 'UNDO'}


    rule_type: StringProperty(
        default='material_group'
    )


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        scene = context.scene
        
        if self.rule_type == 'material_group':
            rule_type = scene.seut.material_groups[scene.seut.material_groups_index]
        elif self.rule_type == 'environment_item':
            rule_type = scene.seut.environment_items[scene.seut.environment_items_index]

        rule_type.rules.remove(rule_type.rules_index)

        return {'FINISHED'}


class SEUT_OT_Planet_DistributionRuleLayer_Add(Operator):
    """Adds a Distribution Rule Layer"""
    bl_idname = "planet.add_distribution_rule_layer"
    bl_label = "Add Distribution Rule Layer"
    bl_options = {'REGISTER', 'UNDO'}


    rule_type: StringProperty(
        default='material_group'
    )


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        scene = context.scene
        
        if self.rule_type == 'material_group':
            rule_type = scene.seut.material_groups[scene.seut.material_groups_index]
        elif self.rule_type == 'environment_item':
            rule_type = scene.seut.environment_items[scene.seut.environment_items_index]

        rule = rule_type.rules[rule_type.rules_index]

        item = rule.layers.add()
        item.material = "LayerMaterial"

        return {'FINISHED'}


class SEUT_OT_Planet_DistributionRuleLayer_Remove(Operator):
    """Removes a Distribution Rule Layer"""
    bl_idname = "planet.remove_distribution_rule_layer"
    bl_label = "Remove Distribution Rule Layer"
    bl_options = {'REGISTER', 'UNDO'}


    rule_type: StringProperty(
        default='material_group'
    )


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        scene = context.scene
        
        if self.rule_type == 'material_group':
            rule_type = scene.seut.material_groups[scene.seut.material_groups_index]
        elif self.rule_type == 'environment_item':
            rule_type = scene.seut.environment_items[scene.seut.environment_items_index]

        rule = rule_type.rules[rule_type.rules_index]

        rule.layers.remove(rule.layers_index)

        return {'FINISHED'}


class SEUT_OT_Planet_EnvironmentItem_Add(Operator):
    """Adds an Environment Item"""
    bl_idname = "planet.add_environment_item"
    bl_label = "Add Environment Item"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        scene = context.scene
        
        item = scene.seut.environment_items.add()
        item.name = "EnvironmentItem"

        item = scene.seut.environment_items[scene.seut.environment_items_index].rules.add()
        item.name = "Rule"

        return {'FINISHED'}


class SEUT_OT_Planet_EnvironmentItem_Remove(Operator):
    """Removes an Environment Item"""
    bl_idname = "planet.remove_environment_item"
    bl_label = "Remove Environment Item"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        scene = context.scene

        scene.seut.environment_items.remove(scene.seut.environment_items_index)

        return {'FINISHED'}


class SEUT_OT_Planet_Biome_Add(Operator):
    """Adds a Biome"""
    bl_idname = "planet.add_biome"
    bl_label = "Add Biome"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        
        add_biome(context)

        return {'FINISHED'}


class SEUT_OT_Planet_Biome_Remove(Operator):
    """Removes a Biome"""
    bl_idname = "planet.remove_biome"
    bl_label = "Remove Biome"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        scene = context.scene
        environment_item = scene.seut.environment_items[scene.seut.environment_items_index]

        environment_item.biomes.remove(environment_item.biomes_index)
        
        for c in scene.seut.biomes_palette.colors:
            found = False
            for ei in scene.seut.environment_items:
                for biome in ei.biomes:
                    if biome.value == int(round(c.color[1] * 255)) and c.color[0] == 0 and c.color[2] == 0:
                        found = True
            if not found:
                scene.seut.biomes_palette.colors.remove(c)

        return {'FINISHED'}


class SEUT_OT_Planet_Material_Add(Operator):
    """Adds a Material"""
    bl_idname = "planet.add_material"
    bl_label = "Add Material"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        scene = context.scene
        environment_item = scene.seut.environment_items[scene.seut.environment_items_index]

        item = environment_item.materials.add()
        item.name = "VoxelMaterial"

        return {'FINISHED'}


class SEUT_OT_Planet_Material_Remove(Operator):
    """Removes a Material"""
    bl_idname = "planet.remove_material"
    bl_label = "Remove Material"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        scene = context.scene
        environment_item = scene.seut.environment_items[scene.seut.environment_items_index]

        environment_item.materials.remove(environment_item.materials_index)

        return {'FINISHED'}


class SEUT_OT_Planet_Item_Add(Operator):
    """Adds an Item"""
    bl_idname = "planet.add_item"
    bl_label = "Add Item"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        scene = context.scene
        environment_item = scene.seut.environment_items[scene.seut.environment_items_index]

        item = environment_item.items.add()

        return {'FINISHED'}


class SEUT_OT_Planet_Item_Remove(Operator):
    """Removes an Item"""
    bl_idname = "planet.remove_item"
    bl_label = "Remove Item"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        scene = context.scene
        environment_item = scene.seut.environment_items[scene.seut.environment_items_index]

        environment_item.items.remove(environment_item.items_index)

        return {'FINISHED'}


class SEUT_OT_Planet_OreMappings_Add(Operator):
    """Adds an Ore Mapping to a Planet"""
    bl_idname = "planet.add_ore_mapping"
    bl_label = "Add Ore Mapping"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        
        add_ore_mapping(context)

        return {'FINISHED'}


class SEUT_OT_Planet_OreMappings_Remove(Operator):
    """Removes an Ore Mapping from a Planet"""
    bl_idname = "planet.remove_ore_mapping"
    bl_label = "Remove Ore Mapping"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        scene = context.scene

        scene.seut.ore_mappings.remove(scene.seut.ore_mappings_index)
        
        for c in scene.seut.ore_mappings_palette.colors:
            found = False
            for om in scene.seut.ore_mappings:
                if om.value == int(round(c.color[2] * 255)) and c.color[0] == 0 and c.color[1] == 0:
                    found = True
            if not found:
                scene.seut.ore_mappings_palette.colors.remove(c)

        return {'FINISHED'}


class SEUT_OT_Planet_ExportAll(Operator):
    """Exports all planet data to the Mod Folder"""
    bl_idname = "planet.export_all"
    bl_label = "Export"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        if scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers:
            if not os.path.exists(scene.seut.mod_path):
                Operator.poll_message_set("Mod must first be defined.")
                return False

            return True


    def execute(self, context):
        scene = context.scene

        result_sbc = export_planet_sbc(self, context)
        result_maps = export_planet_maps(scene)

        if result_sbc == {'FINISHED'} and result_maps == {'FINISHED'}:
            result = {'FINISHED'}
        else:
            result = {'CANCELLED'}

        return result


class SEUT_OT_Planet_Bake(Operator):
    """Bakes planet maps and places them in the Mod Folder"""
    bl_idname = "planet.bake"
    bl_label = "Bake"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        if scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers:
            if scene.seut.bake_target is None or scene.seut.bake_source is None:
                Operator.poll_message_set("Bake source or bake target are missing.")
                return False
            return True


    def execute(self, context):

        result = bake_planet_map(context)

        return result


last_dir = ""
valid_files = {}


def items_planet_def(self, context):

    global last_dir
    global valid_files

    if os.path.dirname(self.filepath) == last_dir:
        if self.filepath in valid_files:
            return valid_files[self.filepath]
        else:
            return []

    else:
        for f in os.listdir(os.path.dirname(self.filepath)):
            if os.path.splitext(f)[1] != '.sbc':
                continue
            
            file = os.path.join(os.path.dirname(self.filepath), f)
            with open(file) as f_open:
                if '<TypeId>PlanetGeneratorDefinition</TypeId>' in f_open.read():
                    
                    try:
                        tree = ET.parse(file)
                    except:
                        return []

                    root = tree.getroot()
                    if not root.tag == 'Definitions':
                        return []

                    for definition in root:
                        if definition.tag == 'PlanetGeneratorDefinitions':
                            for planet in definition:
                                for elem in planet:
                                    if elem.tag == 'Id':
                                        for elem2 in elem:
                                            if elem2.tag == 'SubtypeId':
                                                if not file in valid_files:
                                                    valid_files[file] = []
                                                valid_files[file].append((elem2.text, elem2.text, ""))
                                                break
                                        break

                        elif definition.tag == 'Definition' and '{http://www.w3.org/2001/XMLSchema-instance}type' in definition.attrib and definition.attrib['{http://www.w3.org/2001/XMLSchema-instance}type'] == 'PlanetGeneratorDefinition':
                            for elem in definition:
                                if elem.tag == 'Id':
                                    for elem2 in elem:
                                        if elem2.tag == 'SubtypeId':
                                            if not file in valid_files:
                                                valid_files[file] = []
                                            valid_files[file].append((elem2.text, elem2.text, ""))
                                            break
                                    break
                                
        last_dir = os.path.dirname(self.filepath)
        if self.filepath in valid_files:
            return valid_files[self.filepath]
        else:
            return []


class SEUT_OT_Planet_ImportSBC(Operator, ImportHelper):
    """Imports a SBC planet definition"""
    bl_idname = "planet.import_sbc"
    bl_label = "Import Planet Definition"
    bl_options = {'REGISTER', 'UNDO'}


    filename_ext = ".sbc"

    filter_glob: StringProperty(
        default='*.sbc',
        options={'HIDDEN'}
    )
    filepath: StringProperty(
        subtype="FILE_PATH"
    )
    planet_def: EnumProperty(
        name='Planet',
        items=items_planet_def,
        default=0
    )
    import_ore_mappings: BoolProperty(
        name="Ore Mappings",
        description="Whether to import Ore Mappings",
        default=True
    )
    import_material_groups: BoolProperty(
        name="Material Groups",
        description="Whether to import Material Groups",
        default=True
    )
    import_environment_items: BoolProperty(
        name="Environment Items",
        description="Whether to import Environment Items",
        default=True
    )


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):

        result = import_planet_sbc(self, context)

        return result


    def draw(self, context):
        layout = self.layout

        box = layout.box()
        row = box.row()
        row.label(text="Options", icon='SETTINGS')

        if not  self.filepath in valid_files:
            row = box.row()
            row.alert = True
            row.label(text="No Planet Definition SBC selected.")

        box.prop(self, 'planet_def')
        col = box.column(align=True)
        col.prop(self, 'import_ore_mappings', icon='TEXTURE_DATA')
        col.prop(self, 'import_material_groups', icon='MATERIAL_DATA')
        col.prop(self, 'import_environment_items', icon='SCENE_DATA')


    def invoke(self, context, event):

        context.window_manager.fileselect_add(self)
        
        return {'RUNNING_MODAL'}