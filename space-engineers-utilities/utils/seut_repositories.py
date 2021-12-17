import bpy
import os
import re
import json
import requests
import webbrowser
import tempfile
import shutil
import zipfile
import glob

from bpy.types              import Operator
from bpy.props              import StringProperty, BoolProperty

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
            webbrowser.open(f"{repo.git_url}/releases/tag/v{repo.latest_version}")
        
        return {'FINISHED'}


class SEUT_OT_CheckUpdate(Operator):
    """Check whether a newer update is available"""
    bl_idname = "wm.check_update"
    bl_label = "Check for Updates"
    bl_options = {'REGISTER', 'UNDO'}


    repo_name: StringProperty()


    def execute(self, context):

        wm = context.window_manager
        repo = wm.seut.repos[self.repo_name]

        check_repo_update(repo)
        
        return {'FINISHED'}


class SEUT_OT_DownloadUpdate(Operator):
    """Downloads and installs the specified repository"""
    bl_idname = "wm.download_update"
    bl_label = "Download & Install"
    bl_options = {'REGISTER', 'UNDO'}


    repo_name: StringProperty()

    wipe: BoolProperty(
        default=False
    )


    def execute(self, context):

        wm = context.window_manager
        repo = wm.seut.repos[self.repo_name]
        
        update_repo(repo, self.wipe)
        
        return {'FINISHED'}


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
        repo.text_name = 'SEUT Assets'
        repo.git_url = "https://github.com/enenra/seut-assets"
        repo.cfg_path = preferences.asset_path
    
    update_repo_from_config(repo)
    
    # MWMB
    if 'MWMBuilder' in wm.seut.repos:
        repo = wm.seut.repos['MWMBuilder']
    else:
        repo = wm.seut.repos.add()
        repo.name = 'MWMBuilder'
        repo.text_name = 'MWM Builder'
        repo.git_url = "https://github.com/cstahlhut/MWMBuilder"
        repo.cfg_path = os.path.join(preferences.asset_path, 'Tools', 'MWMBuilder')
            
    update_repo_from_config(repo)


def update_repo_from_config(repo: object):

    preferences = get_preferences()
    
    if repo.name == 'space-engineers-utilities':
        return

    cfg_path = os.path.join(repo.cfg_path, f"{repo.name}.cfg")
    data = {}
    if os.path.exists(cfg_path):
        with open(cfg_path) as cfg_file:
            data = json.load(cfg_file)

    if repo.name in data:
        cfg = data[repo.name][0]
        if 'current_version' in cfg:
            repo.current_version = cfg['current_version']
        if 'dev_tag' in cfg:
            repo.dev_tag = cfg['dev_tag']
        if 'dev_version' in cfg:
            repo.dev_version = cfg['dev_version']
        if repo.name == 'MWMBuilder':
            preferences.mwmb_path = os.path.join(repo.cfg_path, 'MwmBuilder.exe')

    else:
        repo.update_message = f"{repo.name} not installed."
        repo.current_version = "0.0.0"
        repo.dev_tag = "rc"
        repo.dev_version = 0

        if repo.name == 'MWMBuilder':
            preferences.mwmb_path = ""

    if repo.dev_version > 0:
        repo.dev_mode = True
    else:
        repo.dev_mode = False


def check_all_repo_updates():
    wm = bpy.context.window_manager
    check_repo_update(wm.seut.repos['space-engineers-utilities'])
    check_repo_update(wm.seut.repos['seut-assets'])
    check_repo_update(wm.seut.repos['MWMBuilder'])


def check_repo_update(repo: object):
    """Checks the GitHub API for the latest release of the given repository."""

    repo.needs_update = False
    repo.update_message = ""
    update_repo_from_config(repo)

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
                if current_version == (0, 0, 0):
                    outdated = f"{repo.text_name} not installed."
                else:
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


def update_repo(repo: object, wipe: bool = False):
    
    tag = repo.latest_version
    location = repo.cfg_path
    git_url = repo.git_url.replace("github.com/", "api.github.com/repos/")
    response_releases = requests.get(git_url + "/releases")

    try:
        if response_releases.status_code == 200:
            json_releases = response_releases.json()

            found = False
            download_url = ""
            for release in json_releases:
                if release['tag_name'] == f"v{tag}" and 'assets' in release:
                    for asset in release['assets']:
                        if asset['name'].endswith(".zip"):
                            download_url = asset['browser_download_url']
                            found = True
                            break
                        
            if found:
                temp_dir = tempfile.mkdtemp()
                download_path = os.path.join(temp_dir, f"{repo.name}_{tag}.zip")

                try:
                    downloaded_dir = download_copy(download_url, temp_dir, download_path, repo)

                    if wipe:
                        if os.path.exists(location):
                            shutil.rmtree(location)
                        shutil.copytree(downloaded_dir, location)
                    else:
                        move_files_recursive(downloaded_dir, location)

                    shutil.rmtree(temp_dir)

                except Exception as e:
                    print(e)
                    shutil.rmtree(temp_dir)
                    return {'CANCELLED'}

                check_repo_update(repo)
                return {'FINISHED'}

            else:
                repo.update_message = "Release could not be found."
                return {'CANCELLED'}
            

        elif response_releases.status_code == 403:
            repo.update_message = "Rate limit exceeded!"
            return {'CANCELLED'}

        else:
            repo.update_message = "Release could not be found."


    except Exception as e:
        print(e)
        repo.update_message = "Connection Failed!"
        return {'CANCELLED'}


def download_copy(url, directory, save_path, repo, chunk_size=128):
    r = requests.get(url, stream=True)
    with open(save_path, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)

    with zipfile.ZipFile(save_path, 'r') as zip_ref:
        zip_ref.extractall(directory)
    
    os.remove(save_path)

    init = glob.glob(directory + f"/**/{repo.name}.cfg", recursive = True)[0]

    return os.path.dirname(init)


def move_files_recursive(source: str, destination: str):

    if not os.path.exists(destination):
        shutil.move(source, destination)

    else:
        for root, dirs, files in os.walk(source):

            for item in files:
                src_file = os.path.join(source, item)
                dst_file = os.path.join(destination, item)
                if os.path.exists(dst_file):
                    os.remove(dst_file)
                shutil.move(src_file, dst_file)

            for item in dirs:
                src_dir = os.path.join(source, item)
                dest_dir = os.path.join(destination, item)
                move_files_recursive(src_dir, dest_dir)