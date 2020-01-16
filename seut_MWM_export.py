def mwmbuilder(self, settings: ExportSettings, fbxfile: str, havokfile: str, paramsfile: str, mwmfile: str):
    if not settings.isRunMwmbuilder:
        if settings.isLogToolOutput:
            write_to_log(mwmfile+'.log', b"mwmbuilder skipped.")
        return

    mwmargs = bpy.context.user_preferences.addons[__package__].preferences.mwmbuildercmdarg.strip()
    extracmds = mwmargs.split(" ")
    
    contentDir = join(settings.mwmDir, 'Sources')
    os.makedirs(contentDir, exist_ok = True)
    basename = os.path.splitext(os.path.basename(mwmfile))[0]

    def copy(srcfile: str, dstfile: str):
        if not srcfile is None and dstfile != srcfile:
            shutil.copy2(srcfile, dstfile)

    copy(fbxfile, join(contentDir, basename + '.fbx'))
    copy(paramsfile, join(contentDir, basename + '.xml'))
    copy(havokfile, join(contentDir, basename + '.hkt'))

    if settings.useactualmwmbuilder:
        cmdline = [settings.mwmbuilderactual, '/s:Sources', '/m:'+basename+'.fbx', '/o:.\\']
    elif settings.isEkmwmbuilder:
        cmdline = [settings.mwmbuilder, '/s:Sources', '/m:'+basename+'.fbx', '/o:.\\' , '/x:'+settings.materialref , '/lod:'+settings.lodsmwmDir]
    else:
        cmdline = [settings.mwmbuilder, '/s:Sources', '/m:'+basename+'.fbx', '/o:.\\']

    if extracmds:
        for cmd in extracmds:
            if not cmd.strip() == "" and not cmd == " ":
                cmdline.append(cmd)

    def checkForLoggedErrors(logtext):
        if b": ERROR:" in logtext:
            raise MissbehavingToolError('MwmBuilder failed without an appropriate exit-code. Please check the log-file.')

    settings.callTool(cmdline, cwd=settings.mwmDir, logfile=mwmfile+'.log', logtextInspector=checkForLoggedErrors)
    copy(join(settings.mwmDir, basename + '.mwm'), mwmfile)