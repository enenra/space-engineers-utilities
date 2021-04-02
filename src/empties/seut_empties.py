import bpy

from bpy.types  import Operator, Menu, UIList, PropertyGroup, Panel
from bpy.props  import PointerProperty, IntProperty, StringProperty


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
        return bpy.context.view_layer.objects.active.type == 'EMPTY' and ('file' in bpy.context.view_layer.objects.active or 'highlight' in bpy.context.view_layer.objects.active)


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        empty = context.view_layer.objects.active

        if 'file' in empty:
            row = layout.row()
            row.label(text="Subpart Scene:", icon = 'EMPTY_DATA')

            col = row.column(align=True)
            link = col.operator('wm.semref_link', text="", icon='INFO')
            link.section = 'tutorials/'
            link.page = 'subparts'
            
            layout.prop(empty.seut, 'linkedScene', text="",)

        elif 'highlight' in empty:
            
            row = layout.row()
            row.label(text="Highlight Objects:", icon = 'EMPTY_DATA')
            
            col = row.column(align=True)
            link = col.operator('wm.semref_link', text="", icon='INFO')
            link.section = 'tutorials/'
            link.page = 'interaction-highlights'

            layout.operator("object.highlight_object_add", text="Add")

            if len(empty.seut.highlight_objects) > 0:
                box = layout.box()

                for idx in range(0, len(empty.seut.highlight_objects)):
                    row = box.row()
                    row.prop(empty.seut.highlight_objects[idx], 'obj', text = '')

                    col = row.column(align = True)
                    remove = col.operator('object.highlight_object_remove', icon = 'REMOVE', text = "", emboss = False)
                    remove.idx = idx