import bpy
import bmesh

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

from ..seut_collections             import get_collections


class SEUT_OT_QuickTools_BS_ApplyConstruction(Operator):
    """Applies a 'Construction'-type material to all selected objects"""
    bl_idname = "quicktools.apply_construction_material"
    bl_label = "Apply 'Construction' Material"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene

        if 'Construction' not in bpy.data.materials:
            Operator.poll_message_set("Material 'Construction' not found. Link it to this BLEND-file to use this operator.")
            return False

        return 'SEUT' in scene.view_layers


    def execute(self, context):

        for obj in context.selected_objects:
            for slot in obj.material_slots:

                if slot.material.name.endswith("_Colorable"):
                    name = f"{slot.material.name[:-len('_Colorable')]}_Chrome"
                    if name in bpy.data.materials:
                        slot.material = bpy.data.materials[name]
                    else:
                        slot.material = bpy.data.materials['Construction']

                elif slot.material.name.endswith("_Darker"):
                    name = f"{slot.material.name[:-len('_Darker')]}_Chrome"
                    if name in bpy.data.materials:
                        slot.material = bpy.data.materials[name]
                    else:
                        slot.material = bpy.data.materials['Construction']

                else:
                    slot.material = bpy.data.materials['Construction']

        return {'FINISHED'}


class SEUT_OT_QuickTools_BS_CutAndSolidify(Operator):
    """Uses Inset faces with given distance, deletes the inner faces and then applies a Solidify modifier with given thickness and applies it"""
    bl_idname = "quicktools.cut_and_solidify"
    bl_label = "Cut and Solidify"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene

        if context.active_object is None:
            return False

        if context.active_object.mode != 'EDIT':
            Operator.poll_message_set("Must be in edit mode.")
            return False

        bm = bmesh.from_edit_mesh(context.active_object.data)

        if len([f for f in bm.faces if f.select]) < 1:
            Operator.poll_message_set("Must have faces selected to run this operator.")
            return False

        return 'SEUT' in scene.view_layers


    inset_thickness: FloatProperty(
        name="Inset Thickness",
        default=0.025
    )
    solidify_thickness: FloatProperty(
        name="Solidify Thickness",
        default=0.015
    )


    def execute(self, context):
        obj = context.view_layer.objects.active

        bpy.ops.mesh.inset(thickness=self.inset_thickness, depth=0, use_individual=True, release_confirm=True)
        bpy.ops.mesh.delete(type='FACE')

        mods = {m.name for m in obj.modifiers}
        bpy.ops.object.modifier_add(type='SOLIDIFY')
        mods_new = {m.name for m in obj.modifiers}

        if len(mods) < 1:
            mod_name = list(mods_new)[0]
        else:
            mod_name = list(mods_new - mods)[0]

        modifier = obj.modifiers[mod_name]
        modifier.thickness = self.solidify_thickness

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.modifier_apply(modifier="Solidify")
        bpy.ops.object.mode_set(mode='EDIT')

        bm = bmesh.from_edit_mesh(context.active_object.data)
        for f in bm.faces:
            f.select = True
        bpy.ops.mesh.select_mode(type='FACE')

        return {'FINISHED'}


    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.prop(self, "inset_thickness")
        col.prop(self, "solidify_thickness")


class SEUT_OT_QuickTools_GEN_OriginToSelected(Operator):
    """Sets the origin of the current object to the selected vertice, edge or face"""
    bl_idname = "quicktools.origin_to_selected"
    bl_label = "Origin to Selected"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene

        if context.active_object is None:
            return False

        if context.active_object.mode != 'EDIT':
            Operator.poll_message_set("Must be in edit mode.")
            return False

        bm = bmesh.from_edit_mesh(context.active_object.data)

        verts = len([v for v in bm.verts if v.select])
        edges = len([e for e in bm.edges if e.select])
        faces = len([f for f in bm.faces if f.select])

        if (bm.select_mode == 'VERT' and verts != 1) or (bm.select_mode == 'EDGE' and edges != 1) or (bm.select_mode == 'FACE' and faces != 1):
            Operator.poll_message_set("Must have one item selected to run this operator.")
            return False

        return 'SEUT' in scene.view_layers


    def execute(self, context):

        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
        bpy.ops.view3d.snap_cursor_to_center()
        bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'}


class SEUT_OT_QuickTools_GEN_MirrorAndApply(Operator):
    """Mirrors all selected objects, then applies transformations and flips normals"""
    bl_idname = "quicktools.mirror_apply"
    bl_label = "Mirror And Apply"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene

        if context.active_object is None:
            return False

        if context.active_object.mode != 'OBJECT':
            Operator.poll_message_set("Must be in object mode.")
            return False

        return 'SEUT' in scene.view_layers


    axis: EnumProperty(
        name="Mirror Axis",
        description="The axis on which to mirror the selected objects on",
        items=(
            ('x', 'X', ''),
            ('y', 'Y', ''),
            ('z', 'Z', '')
            ),
        default='x',
    )


    def execute(self, context):

        if context.active_object.type != 'MESH':
            return {'CANCELLED'}

        bpy.ops.transform.mirror(
            orient_type='GLOBAL',
            orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            orient_matrix_type='GLOBAL',
            constraint_axis=(self.axis == 'x', self.axis == 'y', self.axis == 'z')
        )
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.object.mode_set(mode='EDIT')
        for obj in context.selected_objects:
            bm = bmesh.from_edit_mesh(obj.data)
            for f in bm.faces:
                f.select = True
        bpy.ops.mesh.flip_normals()
        bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}


class SEUT_OT_QuickTools_MAIN_AddBevels(Operator):
    """Adds bevels of a given amount to all selected objects"""
    bl_idname = "quicktools.add_bevels"
    bl_label = "Add Bevels"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene

        if context.active_object is None:
            return False

        if context.active_object.mode != 'OBJECT':
            Operator.poll_message_set("Must be in object mode.")
            return False

        return 'SEUT' in scene.view_layers


    bevel_amount: FloatProperty(
        name="Bevel Amount",
        default=0.0025
    )


    def execute(self, context):

        for obj in context.selected_objects:
            context.view_layer.objects.active = obj

            if bpy.app.version < (4, 1, 0):
                bpy.ops.object.shade_smooth(use_auto_smooth=True)
            else:
                bpy.ops.object.shade_smooth_by_angle()

            mods = {m.name for m in obj.modifiers}
            bpy.ops.object.modifier_add(type='BEVEL')
            mods_new = {m.name for m in obj.modifiers}

            if len(mods) < 1:
                mod_name = list(mods_new)[0]
            else:
                mod_name = list(mods_new - mods)[0]

            modifier = obj.modifiers[mod_name]
            modifier.width = 0.0025
            modifier.harden_normals = True

        return {'FINISHED'}


class SEUT_OT_QuickTools_LOD_RemoveBevels(Operator):
    """Removes all bevels from all selected objects"""
    bl_idname = "quicktools.remove_bevels"
    bl_label = "Remove Bevels"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene

        if context.active_object is None:
            return False

        if context.active_object.mode != 'OBJECT':
            Operator.poll_message_set("Must be in object mode.")
            return False

        return 'SEUT' in scene.view_layers


    def execute(self, context):
        context.view_layer.objects.active = context.active_object

        for obj in context.selected_objects:
            for mod in obj.modifiers:
                if mod.type == 'BEVEL':
                    obj.modifiers.remove(mod)

        return {'FINISHED'}


class SEUT_OT_QuickTools_HKT_ApplyTransforms(Operator):
    """Applies all transformations to objects with rigid bodies by first removing the rigid bodies and then appliying transformations"""
    bl_idname = "quicktools.apply_transforms"
    bl_label = "Apply Transformations"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        scene = context.scene

        if context.active_object is None:
            return False

        if context.active_object.mode != 'OBJECT':
            Operator.poll_message_set("Must be in object mode.")
            return False

        return 'SEUT' in scene.view_layers


    def execute(self, context):
        context.view_layer.objects.active = context.active_object

        for obj in context.selected_objects:
            context.view_layer.objects.active = obj
            bpy.ops.rigidbody.object_remove()

        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        return {'FINISHED'}