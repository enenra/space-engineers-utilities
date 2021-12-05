import bpy
import os
import re
import json
import requests
import webbrowser

from bpy.types              import Operator
from bpy.props              import StringProperty

from ..seut_utils           import get_preferences, get_addon


rel_ver = re.compile(r"v[0-9]+\.[0-9]+\.[0-9]+$")
dev_ver = re.compile(r"v[0-9]+\.[0-9]+\.[0-9]+\-\w+\.[0-9]{1,}$")

tags = {
    'dev': 0,
    'alpha': 1,
    'beta': 2,
    'rc': 3
}


class SEUT_OT_GetUpdate(Operator):
    """Opens the webpage of the latest release"""
    bl_idname = "wm.get_update"
    bl_label = "Get Update"
    bl_options = {'REGISTER', 'UNDO'}


    repo_name: StringProperty()


    def execute(self, context):

        wm = context.window_manager
        repo = wm.seut.repos[self.repo_name]

        if repo.latest_version == "":
            webbrowser.open(f"{repo.git_url}/releases/")
        else:
            webbrowser.open(f"{repo.git_url}/releases/tag/{repo.latest_version}")
        
        return {'FINISHED'}


# TODO: How to deal with where to place and what to replace

def update_register_repos():

    wm = bpy.context.window_manager
    preferences = get_preferences()
    addon = get_addon()

    # SEUT
    if 'space-engineers-utilities' in wm.seut.repos:
        repo = wm.seut.repos['space-engineers-utilities']
    else:
        repo = wm.seut.repos.add()
        repo.name = 'space-engineers-utilities'
        repo.text_name = 'SEUT'
        repo.git_url = addon.bl_info['git_url']
        
    repo.current_version = str(addon.bl_info['version'])[1:-1].replace(', ', '.')
    repo.dev_tag = addon.bl_info['dev_tag']
    repo.dev_version = addon.bl_info['dev_version']
    if repo.dev_version > 0:
        repo.dev_mode = True
    else:
        repo.dev_mode = False

    # SEUT Assets
    if 'seut-assets' in wm.seut.repos:
        repo = wm.seut.repos['seut-assets']
    else:
        repo = wm.seut.repos.add()
        repo.name = 'seut-assets'
        repo.text_name = 'SEUT Assets Repository'
        repo.git_url = "https://github.com/enenra/seut-assets"
    
    path = os.path.join(preferences.asset_path, 'seut-assets.cfg')
    data = {}
    if os.path.exists(path):
        with open(path) as cfg_file:
            data = json.load(cfg_file)

    if 'seut-assets' in data:
        cfg = data['seut-assets'][0]
        if 'current_version' in cfg:
            repo.current_version = cfg['current_version']
        if 'dev_tag' in cfg:
            repo.dev_tag = cfg['dev_tag']
        if 'dev_version' in cfg:
            repo.dev_version = cfg['dev_version']
    else:
        repo.current_version = "0.0.0"
        repo.dev_tag = "rc"
        repo.dev_version = 0
    if repo.dev_version > 0:
        repo.dev_mode = True
    else:
        repo.dev_mode = False
    
    # MWMB
    if 'MWMBuilder' in wm.seut.repos:
        repo = wm.seut.repos['MWMBuilder']
    else:
        repo = wm.seut.repos.add()
        repo.name = 'MWMBuilder'
        repo.text_name = 'MWM Builder'
        repo.git_url = "https://github.com/cstahlhut/MWMBuilder"
            
    path = os.path.join(preferences.asset_path, 'Tools', 'MWMB', 'MWMBuilder.cfg')
    data = {}
    if os.path.exists(path):
        with open(path) as cfg_file:
            data = json.load(cfg_file)
    if 'MWMBuilder' in data:
        cfg = data['MWMBuilder'][0]
        if 'current_version' in cfg:
            repo.current_version = tuple(map(int, cfg['current_version'].split('.')))
        if 'dev_tag' in cfg:
            repo.dev_tag = cfg['dev_tag']
        if 'dev_version' in cfg:
            repo.dev_version = cfg['dev_version']
    else:
        repo.current_version = "0.0.0"
        repo.dev_tag = "rc"
        repo.dev_version = 0
    if repo.dev_version > 0:
        repo.dev_mode = True
    else:
        repo.dev_mode = False


def check_repo_update(repository):
    """Checks the GitHub API for the latest release of the given repository."""

    wm = bpy.context.window_manager
    preferences = get_preferences()
    repo = wm.seut.repos[repository]

    repo.needs_update = False
    repo.update_message = ""

    user_reponame = repo.git_url[len("https://github.com/"):]
    url_tags = f"https://api.github.com/repos/{user_reponame}/tags"
    url_releases = f"https://api.github.com/repos/{user_reponame}/releases"
    current_version = tuple(map(int, repo.current_version.split('.')))
    
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

                        if prerelease and repo.dev_mode:
                            if dev_ver.match(name_tag):
                                versions.append(name_tag)

                        elif not prerelease:
                            if rel_ver.match(name_tag):
                                versions.append(name_tag)
                        break

            if versions == []:
                repo.update_message = "No valid releases found."
                return

            latest_version_name = sorted(versions, reverse=True)[0][1:]

            is_dev = -1
            if dev_ver.match("v" + latest_version_name):
                is_dev = int(re.search("(\d+)(?!.*\d)", latest_version_name)[0])
                dev_tag = latest_version_name[latest_version_name.find("-") + 1:]
                dev_tag = dev_tag[:dev_tag.find(".")]

                if dev_tag not in tags:
                    is_dev = -1

                latest_version = tuple(map(int, latest_version_name.split('-')[0].split('.')))

            else:
                latest_version = tuple(map(int, latest_version_name.split('.')))

            current_version = tuple(current_version)
            repo.latest_version = latest_version_name
            
            if current_version < latest_version:
                outdated = f"{repo.text_name} version {latest_version_name} available!"
                repo.update_message = outdated
                repo.needs_update = True

            elif current_version > latest_version:
                repo.update_message = "Latest development version."
                repo.needs_update = False

            else:
                if repo.dev_mode:
                    
                    # Version number is the same and latest is not a dev version.
                    if is_dev == -1:
                        outdated = f"{repo.text_name} {latest_version_name} (release version) available!"
                        repo.update_message = outdated
                        repo.needs_update = True

                    # Version number is the same but latest is a newer dev version.
                    elif tags[repo.dev_tag] < tags[dev_tag] or tags[repo.dev_tag] == tags[dev_tag] and repo.dev_version < is_dev:
                        outdated = f"{repo.text_name} {latest_version_name} available!"
                        repo.update_message = outdated
                        repo.needs_update = True

                    # Version number is the same, latest is dev build but not newer.
                    else:
                        repo.update_message = "Latest development version."
                        repo.needs_update = False

                else:
                    repo.update_message = f"{repo.text_name} is up to date."
                    repo.needs_update = False
        
        elif response_tags.status_code == 403 or response_releases.status_code == 403:
            repo.update_message = "Rate limit exceeded!"
        
        else:
            repo.update_message = "No valid releases found."

    except Exception as e:
        print(e)
        repo.update_message = "Connection Failed!"