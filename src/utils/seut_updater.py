import bpy
import re
import requests


url = "http://api.github.com/repos/enenra/space-engineers-utilities/tags"

version = re.compile(r"v[0-9] + \.[0-9] + \.[0-9] + ")


def checkUpdate(current_version):
    """Checks the GitHub API for the latest SEUT release"""

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

            latest_version_name = sorted(versions, reverse=True)[0]
            wm.seut.latest_version = latest_version_name
            current_version_name = 'v' + str(current_version).replace("(", "").replace(")", "").replace(", ", ".")
            
            if tuple(current_version_name[1:]) < tuple(str(latest_version_name)[1:]):
                outdated = f"SEUT {latest_version_name[1:]} available!"
                wm.seut.needs_update = outdated

            elif tuple(current_version_name[1:]) > tuple(str(latest_version_name)[1:]):
                wm.seut.needs_update = "Development Build"

            else:
                wm.seut.needs_update = "SEUT is up to date."
        
        elif response.status_code == 403:
            wm.seut.needs_update = "Rate limit exceeded!"

    except:
        wm.seut.needs_update = "Connection Failed!"