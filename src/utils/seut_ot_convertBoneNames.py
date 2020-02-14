import bpy
import re
import os

from bpy.types import Operator

class SEUT_OT_ConvertBonesToBlenderFormat(Operator):
    """Make Bone names Blender compatible"""
    bl_idname = "object.convertbonestoblenderformat"
    bl_label = "Make Blender compatible"
    bl_options = {'REGISTER', 'UNDO'}

    # Greys the button out if there is no active object.
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) != 0

    def execute(self, context):
        """Make Bone names Blender compatible"""

        exlcudedBoneNames = ["SE_RigPelvis", "SE_RigSpine1", "SE_RigSpine2",
                            "SE_RigSpine3", "SE_RigSpine4", "SE_RigRibcage",
                            "SE_RigNeck", "SE_RigRibcageBone001"]
        
        armature = context.object
        
        if armature == None or armature.type is None or not armature:
            self.report({'ERROR'}, "SEUT: Object is not an Armature. (100)")
            print("No object selected.")
            return {'CANCELLED'}
        
        if armature.type == None or armature.type is None or armature.type != 'ARMATURE':
            self.report({'ERROR'}, "SEUT: No Armature selected. (101)")
            print("Object is not an armature.")
            return {'CANCELLED'}
        
        # Renaming patterns
        # Keen example: SE_RigLThigh
        # Blender example: Thigh_L
        patterns = {
            "source_to_blender": "SE_Rig([LR])(.*)", #	"source_to_blender": "ValveBiped\.Bip01_([LR])_(.*)",        
        }
        
        # Check for bones with SE Maya naming convention
        bones = armature.data.bones
        for bone in bones:
            var = re.search(patterns['source_to_blender'], bone.name)
            if var != None and bone.name not in exlcudedBoneNames:
                pattern = 'source_to_blender'
                break
        
        total = 0
        renamed = 0
        not_renamed = []
        
        for bone in bones:
            total += 1
            match = re.search(patterns[pattern], bone.name)

            if match != None and bone.name not in exlcudedBoneNames:
                renamed += 1
                match_1 = match.group(1)
                match_2 = match.group(2)
                
                new_name = match_2 + "_" + match_1
                # print(bone.name+" -> "+new_name)            
                
                # Rename bone
                bone.name = new_name
            else:
                not_renamed.append(bone.name)
                
        print("===========================================")
        print(str(renamed)+"/"+str(total)+" bones renamed ("+pattern+")")
        print("-------------------------------------------")
        print("Not renamed:")
        
        for i in not_renamed:
            print(i)
            
            
        self.report({'INFO'}, "SEUT: Changed all Bones names to Blender convention.")
        
        return {'FINISHED'}


class SEUT_OT_ConvertBonesToSEFormat(Operator):
    """Make Bone names SE compatible"""
    bl_idname = "object.convertbonestoseformat"
    bl_label = "Make SE compatible"
    bl_options = {'REGISTER', 'UNDO'}

    # Greys the button out if there is no active object.
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) != 0

    def execute(self, context):
        """Make Bone names SE compatible"""

        exlcudedBoneNames = ["SE_RigPelvis", "SE_RigSpine1", "SE_RigSpine2",
                            "SE_RigSpine3", "SE_RigSpine4", "SE_RigRibcage",
                            "SE_RigNeck", "SE_RigRibcageBone001"]

        os.system("cls")
        armature = bpy.context.object
        if not armature:
            print("No object selected.")
            return {'CANCELLED'}
        
        if armature.type != 'ARMATURE':
            print("Object is not an armature.")
            return {'CANCELLED'}
        
        # Renaming patterns
        # Keen example: SE_RigLThigh
        # Blender example: Thigh_L
        patterns = {
            "blender_to_source": "(.*)(_[LR])" #	"blender_to_source": "ValveBiped\.Bip01_(.*)_([LR])"
        }
        
        # Check for bones with Valve naming convention
        bones = armature.data.bones
        for bone in bones:
            var = re.search(patterns['blender_to_source'], bone.name)
            if var != None and bone.name not in exlcudedBoneNames:
                pattern = 'blender_to_source'
                break
        
        total = 0
        renamed = 0
        not_renamed = []
        
        for bone in bones:
            total += 1
            match = re.search(patterns[pattern], bone.name)

            if match != None and bone.name not in exlcudedBoneNames:
                renamed += 1
                match_1 = match.group(1)
                match_2 = match.group(2)
                
                if match_2.startswith('_'):
                    match_2 = match_2[1 : : ]
                
                # Keen example: SE_RigLThigh
                new_name = "SE_Rig" + match_2 + match_1
                # print(bone.name+" -> "+new_name)            
                
                # Rename bone
                bone.name = new_name
            else:
                not_renamed.append(bone.name)
                
        print("===========================================")
        print(str(renamed)+"/"+str(total)+" bones renamed ("+pattern+")")
        print("-------------------------------------------")
        print("Not renamed:")
        
        for i in not_renamed:
            print(i)            
            
        self.report({'INFO'}, "SEUT: Changed all Bones names to SE convention.")
        
        return {'FINISHED'}