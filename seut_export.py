import bpy
import xml.etree.ElementTree as ET
import xml.dom.minidom


class SEUT_OT_Export(bpy.types.Operator):
    """Exports all enabled file types and collections"""
    bl_idname = "object.export"
    bl_label = "Export"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        scene = context.scene

        # Debug
        print('OT: Export')

        # If no export folder is set, error out.
        if scene.prop_export_exportPath == None:
            print("SEUT Error 003: No export folder defined.")
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

        return {'FINISHED'}


    # Will initially ONLY support MatLib materials!
    def export_XML(context, collection):
        """Exports the XML file for a defined collection"""
        
        # analyze what collection type it is by looking at its name
        

        # create string and add initial nodes
        paramCenteredVal = 'false'
        paramRescaleFactorVal = str(context.scene.prop_export_rescaleFactor)
        paramRescaleToLengthInMetersVal = 'false'




        # set up LOD nodes, depending on what type of collection it is and what LOD collections have children

        # iterate through all materials of all objects within the collection and create nodes for them

        # if the material is not a linked material, create material instead of materialref
        # will need to iterate through the image textures of the selected material
        # ========== TODO ==========
        # add support for those custom material paremeters?

        # Create file with subtypename + collection name and write string to it
        # Always create on blend file location?

        return

    
    def export_FBX(context, collection):
        """Exports the FBX file for a defined collection"""

        # Copy dummies over if not present as safety? to LOD1 for sure, but are they needed in LOD2?

        # What happens if there's multiple objects in the collection? Can I input a collection into the export operator?

        return