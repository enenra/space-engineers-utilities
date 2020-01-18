from .seut_ot_export        import ExportSettings

def mwmbuilder(self, path, settings: ExportSettings, fbxfile: str, havokfile: str, paramsfile: str, mwmfile: str):

    cmdline = [settings.mwmbuilder, '/f', '/s:.\\', '/o:.\\Models', '/l:.\\log.log', '/x:D:\\Steam\\SteamApps\\common\\SpaceEngineersModSDK\\OriginalContent\\Materials']
    # cmdline = [settings.mwmbuilder, '/s:Sources', '/m:'+basename+'.fbx', '/o:.\\' , '/x:'+settings.materialref , '/lod:'+settings.lodsmwmDir]
    settings.callTool(cmdline, cwd=path, logfile=mwmfile+'.log')