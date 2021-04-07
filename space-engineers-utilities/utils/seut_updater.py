import bpy
import re
import requests
import webbrowser

from bpy.types              import Operator

from ..seut_utils           import get_preferences

url_releases = "https://api.github.com/repos/enenra/space-engineers-utilities/releases"
url_tags = "https://api.github.com/repos/enenra/space-engineers-utilities/tags"
rel_ver = re.compile(r"v[0-9]+\.[0-9]+\.[0-9]+")
dev_ver = re.compile(r"v[0-9]+\.[0-9]+\.[0-9]+\-DEV[0-9]")


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

                        if prerelease and preferences.dev_mode:
                            if dev_ver.match(name_tag):
                                versions.append(name_tag)

                        elif not prerelease:
                            if rel_ver.match(name_tag):
                                versions.append(name_tag)
                        break
            
            # For testing
            # versions.append('v0.9.95')
            
            latest_version_name = sorted(versions, reverse=True)[0][1:]

            is_dev = -1
            if latest_version_name.find("-DEV") != -1:
                is_dev = int(re.search("(\d+)(?!.*\d)", latest_version_name)[0])
                latest_version = tuple(map(int, latest_version_name.split('-')[0].split('.')))
            else:
                latest_version = tuple(map(int, latest_version_name.split('.')))

            current_version = tuple(current_version)
            wm.seut.latest_version = latest_version_name
            
            if current_version < latest_version:
                outdated = f"SEUT {latest_version_name} available!"
                wm.seut.update_message = outdated
                wm.seut.needs_update = True

            elif current_version > latest_version:
                wm.seut.update_message = "Latest development version."
                wm.seut.needs_update = False

            else:
                if preferences.dev_mode:
                    
                    # Version number is the same and latest is not a dev version.
                    if is_dev == -1:
                        outdated = f"SEUT {latest_version_name} (release version) available!"
                        wm.seut.update_message = outdated
                        wm.seut.needs_update = True

                    # Version number is the same but latest is a newer dev version.
                    elif preferences.dev_ver < is_dev:
                        outdated = f"SEUT {latest_version_name} available!"
                        wm.seut.update_message = outdated
                        wm.seut.needs_update = True

                    # Version number is the same, latest is dev build but not newer.
                    else:
                        wm.seut.update_message = "Latest development version."
                        wm.seut.needs_update = False

                else:
                    wm.seut.update_message = "SEUT is up to date."
                    wm.seut.needs_update = False
        
        elif response_tags.status_code == 403 or response_releases.status_code == 403:
            wm.seut.update_message = "Rate limit exceeded!"

    except:
        wm.seut.update_message = "Connection Failed!"