import bpy
import xml.etree.ElementTree as ET
import xml.dom.minidom

from .seut_recreateCollections    import SEUT_OT_RecreateCollections

class SEUT_OT_Export(bpy.types.Operator):
    """Exports all enabled file types and collections"""
    bl_idname = "object.export"
    bl_label = "Export"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        scene = context.scene

        # Debug
        print('OT: Export')

        # If no SubtypeId is set, error out.
        if scene.prop_subtypeId == "":
            print("SEUT Error 004: No SubtypeId set.")
            return {'CANCELLED'}

        """ TODO: Re-enable after testing is done!
        # If no export folder is set, error out.
        if scene.prop_export_exportPath == "":
            print("SEUT Error 003: No export folder defined.")
            return {'CANCELLED'}
        """

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

        scene = context.scene
        collections = SEUT_OT_RecreateCollections.get_Collections()
        
        # analyze what collection type it is by looking at its name

        # Make sure the collection isn't empty
        

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
        paramRescaleToLengthInMeters.text ='false'

        # iterate through all materials of all objects within the collection and create nodes for them

        # if the material is not a linked material, create material instead of materialref
        # will need to iterate through the image textures of the selected material
        # ========== TODO ==========
        # add support for those custom material paremeters?
        
        # set up LOD nodes, depending on what type of collection it is and what LOD collections have children

        # ========== TODO ==========
        # Should LOD2 and 3 be generated if there is no LOD1? probably a good sanity check to implement.

        # Only add LODs to XML if exporting the main collection, the LOD collections exist and are not empty.
        if collection == collections['main']:
            
            lod1Printed = False
            lod2Printed = False

            if collections['lod1'] == None or len(collections['lod1'].objects) == 0:
                print("SEUT Info: Collection 'LOD1' not found or empty. Skipping.")
            else:
                lod1 = ET.SubElement(model, 'LOD')
                lod1.set('Distance', str(scene.prop_export_lod1Distance))
                lod1Model = ET.SubElement(lod1, 'Model')
                lod1Model.text = scene.prop_subtypeId + '_LOD1'
                lod1Printed = True

            if collections['lod2'] == None or len(collections['lod2'].objects) == 0:
                print("SEUT Info: Collection 'LOD2' not found or empty. Skipping.")
            else:
                if lod1Printed: 
                    lod2 = ET.SubElement(model, 'LOD')
                    lod2.set('Distance', str(scene.prop_export_lod2Distance))
                    lod2Model = ET.SubElement(lod2, 'Model')
                    lod2Model.text = scene.prop_subtypeId + '_LOD2'
                    lod2Printed = True
                else:
                    print("SEUT Error 006: LOD2 cannot be set if LOD1 is not.")

            if collections['lod3'] == None or len(collections['lod3'].objects) == 0:
                print("SEUT Info: Collection 'LOD3' not found or empty. Skipping.")
            else:
                if lod1Printed and lod2Printed:
                    lod3 = ET.SubElement(model, 'LOD')
                    lod3.set('Distance', str(scene.prop_export_lod3Distance))
                    lod3Model = ET.SubElement(lod3, 'Model')
                    lod3Model.text = scene.prop_subtypeId + '_LOD3'
                else:
                    print("SEUT Error 006: LOD3 cannot be set if LOD1 or LOD2 is not.")


        # Create file with subtypename + collection name and write string to it

        xmlString = xml.dom.minidom.parseString(ET.tostring(model))
        xmlFormatted = xmlString.toprettyxml()
        print(xmlFormatted)
        """
        xml = open(scene.prop_export_subtypeId + ".xml", "w")           # probably need to change stuff here
        xml.write(xmlFormatted)
        """

        return

    
    def export_FBX(context, collection):
        """Exports the FBX file for a defined collection"""

        # Copy dummies over if not present as safety? to LOD1 for sure, but are they needed in LOD2?

        # What happens if there's multiple objects in the collection? Can I input a collection into the export operator?

        return