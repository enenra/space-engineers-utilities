import bpy
import os

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
            if scene.seut.planet is not None or scene.seut.planet_preview is not None:
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
            seut_report(self, context, 'ERROR', True, 'E049')
            return {'CANCELLED'}

        if not 'main' in collections or collections['main'] == [] or collections['main'][0] is None:
            seut_report(self, context, 'ERROR', True, 'E049')
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

        if scene.seut.planet is None:
            appended_obj = append_object(context, file_path, 'Planet')
            if appended_obj == -1:
                seut_report(self, context, 'ERROR', True, 'E049')
                return {'CANCELLED'}
            else:
                scene.seut.planet = appended_obj

        if scene.seut.planet_preview is None:
            appended_obj = append_object(context, file_path, 'Preview')
            if appended_obj == -1:
                seut_report(self, context, 'ERROR', True, 'E049')
                return {'CANCELLED'}
            else:
                scene.seut.planet_preview = appended_obj

        mats = ['front', 'back', 'right', 'left', 'up', 'down']
        for mat in bpy.data.materials:
            if mat.name in mats:
                mat.use_fake_user = True

        return {'FINISHED'}


class SEUT_OT_Planet_UIList_Add(Operator):
    """Adds an entry"""
    bl_idname = "planet.uilist_add"
    bl_label = "Add Entry"
    bl_options = {'UNDO'}

    uilist: EnumProperty(
        items=(
            ('material_group', '', ''),
            ('distribution_rule', '', ''),
            ('distribution_rule_layer', '', ''),
            ('environment_item', '', ''),
            ('biome', '', ''),
            ('planet_material', '', ''),
            ('planet_item', '', ''),
            ('ore_mapping', '', ''),
            ('weather_generator', '', ''),
            ('weather', '', ''),
            ),
        default='material_group'
    )
    rule_type: EnumProperty(
        items=(
            ('material_group', '', ''),
            ('environment_item', '', ''),
            ),
        default='material_group'
    )

    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        scene = context.scene

        # material_group
        if self.uilist == 'material_group':
            add_material_group(context)

        # distribution_rule
        elif self.uilist == 'distribution_rule':
            if self.rule_type == 'material_group':
                rule_type = scene.seut.material_groups[scene.seut.material_groups_index]
            elif self.rule_type == 'environment_item':
                rule_type = scene.seut.environment_items[scene.seut.environment_items_index]

            item = rule_type.rules.add()
            item.name = "Rule " + str(len(rule_type.rules))
            rule_type.rules_index = len(rule_type.rules) - 1

        # distribution_rule_layer
        elif self.uilist == 'distribution_rule_layer':
            if self.rule_type == 'material_group':
                rule_type = scene.seut.material_groups[scene.seut.material_groups_index]
            elif self.rule_type == 'environment_item':
                rule_type = scene.seut.environment_items[scene.seut.environment_items_index]

            rule = rule_type.rules[rule_type.rules_index]

            item = rule.layers.add()
            item.name = "LayerMaterial"
            rule.layers_index = len(rule.layers) - 1

        # environment_item
        elif self.uilist == 'environment_item':
            item = scene.seut.environment_items.add()
            item.name = f"EnvironmentItem {len(scene.seut.environment_items)}"
            scene.seut.environment_items_index = len(scene.seut.environment_items) - 1

            rule = item.rules.add()
            rule.name = "Rule"

        # biome
        elif self.uilist == 'biome':
            add_biome(context)

        # planet_material
        elif self.uilist == 'planet_material':
            environment_item = scene.seut.environment_items[scene.seut.environment_items_index]
            item = environment_item.materials.add()
            item.name = "VoxelMaterial"
            environment_item.materials_index = len(environment_item.materials) - 1

        # planet_item
        elif self.uilist == 'planet_item':
            environment_item = scene.seut.environment_items[scene.seut.environment_items_index]
            item = environment_item.items.add()
            environment_item.items_index = len(environment_item.items) - 1

        # ore_mapping
        elif self.uilist == 'ore_mapping':
            add_ore_mapping(context)

        # weather_generator
        elif self.uilist == 'weather_generator':
            item = scene.seut.weather_generators.add()
            item.name = f"Weather Generator {len(scene.seut.weather_generators)}"
            scene.seut.weather_generators_index = len(scene.seut.weather_generators) - 1

        # weather
        elif self.uilist == 'weather':
            weather_generator = scene.seut.weather_generators[scene.seut.weather_generators_index]
            weather_generator.weathers.add()
            weather_generator.weathers_index = len(weather_generator.weathers) - 1

        return {'FINISHED'}


class SEUT_OT_Planet_UIList_Remove(Operator):
    """Removes an entry"""
    bl_idname = "planet.uilist_remove"
    bl_label = "Remove Entry"
    bl_options = {'UNDO'}

    uilist: EnumProperty(
        items=(
            ('material_group', '', ''),
            ('distribution_rule', '', ''),
            ('distribution_rule_layer', '', ''),
            ('environment_item', '', ''),
            ('biome', '', ''),
            ('planet_material', '', ''),
            ('planet_item', '', ''),
            ('ore_mapping', '', ''),
            ('weather_generator', '', ''),
            ('weather', '', ''),
            ),
        default='material_group'
    )
    rule_type: EnumProperty(
        items=(
            ('material_group', '', ''),
            ('environment_item', '', ''),
            ),
        default='material_group'
    )

    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        scene = context.scene

        # material_group
        if self.uilist == 'material_group':
            scene.seut.material_groups.remove(scene.seut.material_groups_index)
            scene.seut.material_groups_index = min(max(0, scene.seut.material_groups_index - 1), len(scene.seut.material_groups) - 1)

            for c in scene.seut.material_groups_palette.colors:
                found = any(
                    mg.value == int(round(c.color[0] * 255))
                    and c.color[1] == 0
                    and c.color[2] == 0
                    for mg in scene.seut.material_groups
                )
                if not found:
                    scene.seut.material_groups_palette.colors.remove(c)

        # distribution_rule
        elif self.uilist == 'distribution_rule':
            if self.rule_type == 'material_group':
                rule_type = scene.seut.material_groups[scene.seut.material_groups_index]
            elif self.rule_type == 'environment_item':
                rule_type = scene.seut.environment_items[scene.seut.environment_items_index]

            rule_type.rules.remove(rule_type.rules_index)
            rule_type.rules_index = min(max(0, rule_type.rules_index - 1), len(rule_type.rules) - 1)

        # distribution_rule_layer
        elif self.uilist == 'distribution_rule_layer':
            if self.rule_type == 'material_group':
                rule_type = scene.seut.material_groups[scene.seut.material_groups_index]
            elif self.rule_type == 'environment_item':
                rule_type = scene.seut.environment_items[scene.seut.environment_items_index]

            rule = rule_type.rules[rule_type.rules_index]

            rule.layers.remove(rule.layers_index)
            rule.layers_index = min(max(0, rule.layers_index - 1), len(rule.layers) - 1)

        # environment_item
        elif self.uilist == 'environment_item':
            scene.seut.environment_items.remove(scene.seut.environment_items_index)
            scene.seut.environment_items_index = min(max(0, scene.seut.environment_items_index - 1), len(scene.seut.environment_items) - 1)

        # biome
        elif self.uilist == 'biome':
            environment_item = scene.seut.environment_items[scene.seut.environment_items_index]

            environment_item.biomes.remove(environment_item.biomes_index)
            environment_item.biomes_index = min(max(0, environment_item.biomes_index - 1), len(environment_item.biomes) - 1)

            for c in scene.seut.biomes_palette.colors:
                found = False
                for ei in scene.seut.environment_items:
                    for biome in ei.biomes:
                        if biome.value == int(round(c.color[1] * 255)) and c.color[0] == 0 and c.color[2] == 0:
                            found = True
                if not found:
                    scene.seut.biomes_palette.colors.remove(c)

        # planet_material
        elif self.uilist == 'planet_material':
            environment_item = scene.seut.environment_items[scene.seut.environment_items_index]

            environment_item.materials.remove(environment_item.materials_index)
            environment_item.materials_index = min(max(0, environment_item.materials_index - 1), len(environment_item.materials) - 1)

        # planet_item
        elif self.uilist == 'planet_item':
            environment_item = scene.seut.environment_items[scene.seut.environment_items_index]

            environment_item.items.remove(environment_item.items_index)
            environment_item.items_index = min(max(0, environment_item.items_index - 1), len(environment_item.items) - 1)

        # ore_mapping
        elif self.uilist == 'ore_mapping':
            scene.seut.ore_mappings.remove(scene.seut.ore_mappings_index)
            scene.seut.ore_mappings_index = min(max(0, scene.seut.ore_mappings_index - 1), len(scene.seut.ore_mappings) - 1)

            for c in scene.seut.ore_mappings_palette.colors:
                found = any(
                    om.value == int(round(c.color[2] * 255))
                    and c.color[0] == 0
                    and c.color[1] == 0
                    for om in scene.seut.ore_mappings
                )
                if not found:
                    scene.seut.ore_mappings_palette.colors.remove(c)

        # weather_generator
        elif self.uilist == 'weather_generator':
            scene.seut.weather_generators.remove(scene.seut.weather_generators_index)
            scene.seut.weather_generators_index = min(max(0, scene.seut.weather_generators_index - 1), len(scene.seut.weather_generators) - 1)

        # weather
        elif self.uilist == 'weather':
            weather_generator = scene.seut.weather_generators[scene.seut.weather_generators_index]

            weather_generator.weathers.remove(weather_generator.weathers_index)
            weather_generator.weathers_index = min(max(0, weather_generator.weathers_index - 1), len(weather_generator.weathers) - 1)

        return {'FINISHED'}


class SEUT_OT_Planet_UIList_Move(Operator):
    """Moves an entry"""
    bl_idname = "planet.uilist_move"
    bl_label = "Move Entry"
    bl_options = {'UNDO'}

    uilist: EnumProperty(
        items=(
            ('material_group', '', ''),
            ('distribution_rule', '', ''),
            ('distribution_rule_layer', '', ''),
            ('environment_item', '', ''),
            ('biome', '', ''),
            ('planet_material', '', ''),
            ('planet_item', '', ''),
            ('ore_mapping', '', ''),
            ('weather_generator', '', ''),
            ('weather', '', ''),
            ),
        default='material_group'
    )

    rule_type: EnumProperty(
        items=(
            ('material_group', '', ''),
            ('environment_item', '', ''),
            ),
        default='material_group'
    )

    direction: EnumProperty(
        items=(
            ('UP', '', ''),
            ('DOWN', '', ''),
            ),
        default='UP'
    )

    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):
        scene = context.scene

        def move_item(direction, idx, group, idx_reference):
            if direction == 'UP' and idx >= 1:
                group.move(idx, idx - 1)
                setattr(idx_reference[0], idx_reference[1], idx - 1)
            elif direction == 'DOWN' and idx < len(group) - 1:
                group.move(idx, idx + 1)
                setattr(idx_reference[0], idx_reference[1], idx + 1)

        # material_group
        if self.uilist == 'material_group':
            move_item(self.direction, scene.seut.material_groups_index, scene.seut.material_groups, [scene.seut, 'material_groups_index'])

        # distribution_rule
        elif self.uilist == 'distribution_rule':
            if self.rule_type == 'material_group':
                rule_type = scene.seut.material_groups[scene.seut.material_groups_index]
            elif self.rule_type == 'environment_item':
                rule_type = scene.seut.environment_items[scene.seut.environment_items_index]
            move_item(self.direction, rule_type.rules_index, rule_type.rules, [rule_type, 'rules_index'])

        # distribution_rule_layer
        elif self.uilist == 'distribution_rule_layer':
            if self.rule_type == 'material_group':
                rule_type = scene.seut.material_groups[scene.seut.material_groups_index]
            elif self.rule_type == 'environment_item':
                rule_type = scene.seut.environment_items[scene.seut.environment_items_index]
            rule = rule_type.rules[rule_type.rules_index]
            move_item(self.direction, rule.layers_index, rule.layers, [rule, 'layers_index'])

        # environment_item
        elif self.uilist == 'environment_item':
            move_item(self.direction, scene.seut.environment_items_index, scene.seut.environment_items, [scene.seut, 'environment_items_index'])

        # biome
        elif self.uilist == 'biome':
            ei = scene.seut.environment_items[scene.seut.environment_items_index]
            move_item(self.direction, ei.biomes_index, ei.biomes, [ei, 'biomes_index'])

        # planet_material
        elif self.uilist == 'planet_material':
            ei = scene.seut.environment_items[scene.seut.environment_items_index]
            move_item(self.direction, ei.materials_index, ei.materials, [ei, 'materials_index'])

        # planet_item
        elif self.uilist == 'planet_item':
            ei = scene.seut.environment_items[scene.seut.environment_items_index]
            move_item(self.direction, ei.items_index, ei.items, [ei, "items_index"])

        # ore_mapping
        elif self.uilist == 'ore_mapping':
            move_item(self.direction, scene.seut.ore_mappings_index, scene.seut.ore_mappings, [scene.seut, 'ore_mappings_index'])

        # weather_generator
        elif self.uilist == 'weather_generator':
            move_item(self.direction, scene.seut.weather_generators_index, scene.seut.weather_generators, [scene.seut, 'weather_generators_index'])

        # weather
        elif self.uilist == 'weather':
            wg = scene.seut.weather_generators[scene.seut.weather_generators_index]
            move_item(self.direction, wg.weathers_index, wg.weathers, [wg, "weathers_index"])

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
            if not os.path.exists(get_abs_path(scene.seut.mod_path)):
                Operator.poll_message_set("Mod must first be defined.")
                return False

            return True


    def execute(self, context):
        scene = context.scene

        if scene.seut.export_sbc_type in ['update', 'new']:
            result_sbc = export_planet_sbc(self, context)
        result_maps = export_planet_maps(scene)

        if scene.seut.export_sbc_type in ['update', 'new'] and result_sbc == {'FINISHED'} and result_maps == {'FINISHED'} or scene.seut.export_sbc_type == 'none' and result_maps == {'FINISHED'}:
            result = {'FINISHED'}
        else:
            result = {'CANCELLED'}

        return result


class SEUT_OT_Planet_Bake(Operator):
    """Bakes the selected map type"""
    bl_idname = "planet.bake"
    bl_label = "Bake"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene
        if scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers:
            if scene.seut.planet is None or scene.seut.planet_preview is None:
                Operator.poll_message_set("Bake source or bake target are missing.")
                return False
            return True


    def execute(self, context):

        return bake_planet_map(context)


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
        subtype="FILE_PATH",
        options={'PATH_SUPPORTS_BLEND_RELATIVE'}
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
    import_weather_generators: BoolProperty(
        name="Weather Generators",
        description="Whether to import Weather Generators",
        default=True
    )


    @classmethod
    def poll(cls, context):
        scene = context.scene
        return scene.seut.sceneType == 'planet_editor' and 'SEUT' in scene.view_layers


    def execute(self, context):

        return import_planet_sbc(self, context)


    def draw(self, context):
        layout = self.layout

        box = layout.box()
        row = box.row()
        row.label(text="Options", icon='SETTINGS')

        if self.filepath not in valid_files:
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