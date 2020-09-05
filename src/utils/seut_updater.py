import bpy
import re
import requests

url = "http://api.github.com/repos/enenra/space-engineers-utilities/tags"

version = re.compile(r"v[0-9]+\.[0-9]+\.[0-9]+")

def checkUpdate(currentVersion):

    wm = bpy.context.window_manager

    wm.seut.needs_update = ""

    try:
        response = requests.get(url)
        if response.status_code == 200:
            resp_json = response.json()
            versions = list()
            for tag in resp_json:
                name = tag['name']
                if version.match(name):
                    versions.append(name)
            latestVersionName = sorted(versions, reverse=True)[0]
            wm.seut.latest_version = latestVersionName

            currentVersionName = 'v' + str(currentVersion).replace("(", "").replace(")", "").replace(", ", ".")
            
            if str(currentVersionName) != str(latestVersionName):
                needsUpdate = f"SEUT {latestVersionName[1:]} available!"
                wm.seut.needs_update = needsUpdate
            else:
                wm.seut.needs_update = "SEUT is up to date."
        
        elif response.status_code == 403:
            wm.seut.needs_update = "Rate limit exceeded!"

    except:
        wm.seut.needs_update = "Connection Failed!"