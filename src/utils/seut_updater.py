import bpy
import re
import requests
import webbrowser

from bpy.types              import Operator

from ..seut_utils           import get_preferences

url_releases = "https://api.github.com/repos/enenra/space-engineers-utilities/releases"
url_tags = "https://api.github.com/repos/enenra/space-engineers-utilities/tags"
version = re.compile(r"v[0-9]+\.[0-9]+\.[0-9]+")


class SEUT_OT_GetUpdate(Operator):
    """Opens the webpage of the latest SEUT release"""
    bl_idname = "wm.get_update"
    bl_label = "Get Update"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        wm = context.window_manager

        if wm.seut.latest_version == "":
            webbrowser.open("https://github.com/enenra/space-engineers-utilities/releases/")

        else:
            webbrowser.open("https://github.com/enenra/space-engineers-utilities/releases/tag/" + wm.seut.latest_version)
        
        return {'FINISHED'}


def check_update(current_version):
    """Checks the GitHub API for the latest SEUT release"""

    wm = bpy.context.window_manager
    preferences = get_preferences()

    wm.seut.needs_update = False
    wm.seut.update_message = ""

    try:
        response_tags = requests.get(url_tags)
        response_releases = requests.get(url_releases)

        if response_tags.status_code == 200 and response_releases.status_code == 200:
            json_tags = response_tags.json()
            json_releases = response_releases.json()

            versions = list()

            for tag in json_tags:
                name_tag = tag['name']

                for release in json_releases:
                    name_release = release['tag_name']
                    prerelease = release['prerelease']

                    if name_tag == name_release:
                        if version.match(name_tag) and prerelease == False:
                            versions.append(name_tag)
                        break

            latest_version_name = sorted(versions, reverse=True)[0]
            wm.seut.latest_version = latest_version_name
            current_version_name = 'v' + str(current_version).replace("(", "").replace(")", "").replace(", ", ".")
            
            if tuple(current_version_name[1:]) < tuple(str(latest_version_name)[1:]):
                outdated = f"SEUT {latest_version_name[1:]} available!"
                wm.seut.update_message = outdated
                wm.seut.needs_update = True

            elif tuple(current_version_name[1:]) > tuple(str(latest_version_name)[1:]):
                wm.seut.update_message = "Development Build"
                wm.seut.needs_update = False

            else:
                if preferences.dev_mode:
                    outdated = f"SEUT {latest_version_name[1:]} available!"
                    wm.seut.update_message = outdated
                    wm.seut.needs_update = True
                else:
                    wm.seut.update_message = "SEUT is up to date."
        
        elif response_tags.status_code == 403 or response_releases.status_code == 403:
            wm.seut.update_message = "Rate limit exceeded!"

    except:
        wm.seut.update_message = "Connection Failed!"