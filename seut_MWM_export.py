from .seut_ot_export        import ExportSettings

def mwmbuilder(self, context, path, settings: ExportSettings, fbxfile: str, havokfile: str, paramsfile: str, mwmfile: str, materialspath):

    scene = context.scene
    cmdline = [settings.mwmbuilder, '/f', '/s:.\\', '/m:'+scene.prop_subtypeId+'.fbx', '/o:'+path+'', '/l:.\\MWMBuilder.log', '/x:'+materialspath+'']
    # cmdline = [settings.mwmbuilder, '/s:Sources', '/m:'+basename+'.fbx', '/o:.\\' , '/x:'+settings.materialref , '/lod:'+settings.lodsmwmDir]
    settings.callTool(cmdline, cwd=path, logfile=mwmfile+'.log')