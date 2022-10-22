from distutils.fancy_getopt import wrap_text
import bpy

from bpy.types  import Operator, Menu, UIList, PropertyGroup, Panel
from bpy.props  import PointerProperty, IntProperty, StringProperty

from ..seut_preferences             import empties


empty_types = {
    'subpart_': 'ARROWS',
    'thruster_flame': 'CONE',
    'muzzle_missile': 'CONE',
    'muzzle_projectile': 'CONE',
    'camera': 'CONE',
}


def update_obj(self, context):
    empty = context.active_object

    if empty is not None:
        if 'highlight' in empty:
            empty['highlight'] = None

        if len(empty.seut.highlight_objects) > 0:
            highlights = ""
            for entry in empty.seut.highlight_objects:

                if entry.obj.name.find("_section") == -1 and entry.obj.name.find("subpart") == -1:
                    entry.obj.name = entry.obj.name + "_section"

                if highlights == "":
                    highlights = entry.obj.name
                else:
                    highlights = highlights + ';' + entry.obj.name

            empty['highlight'] = highlights



def poll_obj(self, object):
    empty = bpy.context.active_object
    return object != empty and object.parent == empty.parent


class SEUT_MT_ContextMenu(Menu):
    """Creates the 'Create Emtpy' context menu"""
    bl_idname = "SEUT_MT_ContextMenu"
    bl_label = "    Create Empty"


    def draw(self, context):
        layout = self.layout

        layout.operator('object.add_highlight_empty', text="Add Highlight Empty")
        layout.operator('scene.add_dummy', text="Add Dummy")
        layout.operator('scene.add_preset_subpart', text="Add Preset Subpart")
        layout.operator('scene.add_custom_subpart', text="Add Custom Subpart")


class SEUT_EmptyHighlights(PropertyGroup):
    """List of the objects an empty is set to highlight"""

    obj: PointerProperty(
        type = bpy.types.Object,
        update = update_obj,
        poll = poll_obj
    )
    idx: IntProperty(
        default = 0
    )


class SEUT_OT_HighlightObjectAdd(Operator):
    """Adds Highlight Object to this empty"""
    bl_idname = "object.highlight_object_add"
    bl_label = "Add Highlight Object"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        return context.active_object is not None


    def execute(self, context):
        scene = context.scene
        empty = context.active_object

        empty.seut.highlight_objects.add()        

        return {'FINISHED'}


class SEUT_OT_HighlightObjectRemove(Operator):
    """Removes a Highlight Object from this empty"""
    bl_idname = "object.highlight_object_remove"
    bl_label = "Remove Highlight Object"
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        return context.active_object is not None


    idx: IntProperty()


    def execute(self, context):
        scene = context.scene
        empty = context.active_object

        empty.seut.highlight_objects.remove(self.idx)        

        return {'FINISHED'}


class SEUT_PT_EmptyLink(Panel):
    """Creates the Empty Properties menu"""

    bl_idname = "SEUT_PT_EmptyLink"
    bl_label = "Space Engineers Utilities"
    bl_category = "SEUT"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'


    # Only display this panel if active object is of type empty and has either 'file' or 'highlight' as a custom property
    @classmethod
    def poll(cls, context):

        match = False
        for empty_type in ['dummies', 'highlight_empties', 'preset_subparts']:
            hits = [marker for marker in empties[empty_type] if(marker in bpy.context.view_layer.objects.active.name or marker[:-1] in bpy.context.view_layer.objects.active.name)]
            if len(hits) > 0:
                match = True
                break

        return bpy.context.view_layer.objects.active.type == 'EMPTY' and ('file' in bpy.context.view_layer.objects.active or 'highlight' in bpy.context.view_layer.objects.active) or match


    def draw(self, context):
        layout = self.layout
        empty = context.view_layer.objects.active

        entry = None
        for empty_type in ['dummies', 'highlight_empties', 'preset_subparts']:
            hits = [marker for marker in empties[empty_type] if(marker in empty.name or marker[:-1] in empty.name)]
            if len(hits) > 0:
                entry = hits[0]
                break
        
        if entry is not None:
            box = layout.box()
            box.label(text=empties[empty_type][entry]['name'], icon='EMPTY_DATA')
            
            paragraphs = empties[empty_type][entry]['description'].split('\n')
            
            for p in paragraphs:
                lines = wrap_text(p, int(context.region.width / 7.75))
                for l in lines:
                    row = box.row()
                    row.scale_y = 0.6
                    row.label(text=l)
            
            layout.separator()

        if 'file' in empty:
            row = layout.row()
            if empty.name.find('dummy_character') != -1:
                row.label(text="Animation Scene:", icon = 'ARMATURE_DATA')
            else:
                row.label(text="Subpart Scene:", icon = 'EMPTY_DATA')

            # col = row.column(align=True)
            # link = col.operator('wm.semref_link', text="", icon='INFO')
            # link.section = 'tutorials'
            # link.page = 'subparts'
            
            layout.prop(empty.seut, 'linkedScene', text="",)

        elif 'highlight' in empty:
            
            row = layout.row()
            row.label(text="Highlight Objects:", icon = 'EMPTY_DATA')
            
            col = row.column(align=True)
            link = col.operator('wm.semref_link', text="", icon='INFO')
            link.section = 'tutorials'
            link.page = '6357205/Interaction+Highlight+Tutorial'

            layout.operator("object.highlight_object_add", text="Add")

            if len(empty.seut.highlight_objects) > 0:
                box = layout.box()

                for idx in range(0, len(empty.seut.highlight_objects)):
                    row = box.row()
                    row.prop(empty.seut.highlight_objects[idx], 'obj', text = '')

                    col = row.column(align = True)
                    remove = col.operator('object.highlight_object_remove', icon = 'REMOVE', text = "", emboss = False)
                    remove.idx = idx