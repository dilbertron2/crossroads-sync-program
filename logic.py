import os
import shutil
from http.client import responses
from queue import PriorityQueue
from zipfile import ZipFile

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QFileDialog
from pathlib import Path
from typing import TYPE_CHECKING
from PyQt6.QtGui import QFont, QFontMetrics
import configparser
import requests
import sys

from git.objects.submodule.base import CLONE

# import main

if TYPE_CHECKING:
    from main import MainWindow


config = configparser.ConfigParser()
config.optionxform = str
target_repo_tf2 = "dilbertron2/sourceroads-fastdl-test"
target_repo_csgo = "dilbertron2/sourceroads-fastdl-csgo-test"
target_repo_general = "dilbertron2/sourceroads-fastdl-css-test"
latest_commit_sha_tf2 = ""
latest_commit_sha_csgo = ""
latest_commit_sha_general = ""
last_checked_commit_sha_tf2 = ""
last_checked_commit_sha_csgo = ""
last_checked_commit_sha_general = ""
local_folder = Path().absolute() / "FastDL Content"
api_url = f"https://api.github.com/repos/"
l4d2_dir = r""
tf2_dir = r""
hldms_dir = r""
hl2dm_dir = r""
dods_dir = r""
css_dir = r""
csgo_dir = r""

games_using_tf2_repo = {"TF2"}
games_using_csgo_repo = {"CS:GO"}
games_using_general_repo = {"L4D2", "DoD:S", "HL2:DM", "HLDM:S", "CS:S"}

tf2_repo_diff = None
csgo_repo_diff = None
general_repo_diff = None

files_to_copy_fastdl_tf2 = []
files_to_copy_fastdl_general = []
files_to_copy_fastdl_csgo = []

#TODO read/write individual fastdl repos and what repos each game is for into the ini file
def read_config(self):
    global l4d2_dir, tf2_dir, hldms_dir, hl2dm_dir, dods_dir, css_dir, csgo_dir, target_repo_tf2, target_repo_csgo
    global target_repo_general, last_checked_commit_sha_tf2, last_checked_commit_sha_csgo, last_checked_commit_sha_general


    if Path("config.ini").exists():
        config.read("config.ini")
        user_dirs = "USER.DIRECTORIES"
        repo_info = "REPO"
        config_target_repo_tf2 = config[repo_info].get("TargetRepoTF2", "")
        config_target_repo_csgo = config[repo_info].get("TargetRepoCSGO", "")
        config_target_repo_general = config[repo_info].get("TargetRepoGeneral", "")
        config_last_commit_sha_tf2 = config[repo_info].get("LastCheckedCommitSHATF2", "")
        config_last_commit_sha_csgo = config[repo_info].get("LastCheckedCommitSHACSGO", "")
        config_last_commit_sha_general = config[repo_info].get("LastCheckedCommitSHAGeneral", "")

        # config_games_using_tf2_repo = config[repo_info].get("GamesUsingRepoTF2")
        # config_games_using_csgo_repo = config[repo_info].get("GamesUsingRepoCSGO")
        # config_games_using_general_repo = config[repo_info].get("GamesUsingRepoGeneral")

        config_l4d2_dir = config[user_dirs].get("l4d2Dir", "")
        config_tf2_dir = config[user_dirs].get("tf2Dir", "")
        config_hldms_dir = config[user_dirs].get("hldmsDir", "")
        config_hl2dm_dir = config[user_dirs].get("hl2dmDir", "")
        config_dods_dir = config[user_dirs].get("dodsDir", "")
        config_css_dir = config[user_dirs].get("cssDir", "")
        config_csgo_dir = config[user_dirs].get("csgoDir", "")

        if config_target_repo_tf2:
            target_repo_tf2 = config_target_repo_tf2

        if config_target_repo_csgo:
            target_repo_csgo = config_target_repo_csgo

        if config_target_repo_general:
            target_repo_general = config_target_repo_general

        if config_last_commit_sha_tf2:
            last_checked_commit_sha_tf2 = config_last_commit_sha_tf2

        if config_last_commit_sha_csgo:
            last_checked_commit_sha_csgo = config_last_commit_sha_csgo

        if config_last_commit_sha_general:
            last_checked_commit_sha_general = config_last_commit_sha_general

        # if config_games_using_tf2_repo:
        #     games_using_tf2_repo = set(config_games_using_tf2_repo.split(","))
        #
        # if config_games_using_csgo_repo:
        #     games_using_csgo_repo = set(config_games_using_csgo_repo.split(","))
        #
        # if config_games_using_general_repo:
        #     games_using_general_repo = set(config_games_using_general_repo.split(","))

        if config_l4d2_dir:
            if (Path(config_l4d2_dir) / "left4dead2.exe").exists():
                l4d2_dir = Path(config_l4d2_dir)
                self.ui.L4D2_path_label.setText(str(l4d2_dir))

        if config_tf2_dir:
            if (Path(config_tf2_dir) / "tf.exe").exists():
                tf2_dir = Path(config_tf2_dir)
                self.ui.TF2_path_label.setText(str(tf2_dir))

        if config_hldms_dir:
            if (Path(config_hldms_dir) / "hl1mp.exe").exists():
                hldms_dir = Path(config_hldms_dir)
                self.ui.HLDMS_path_label.setText(str(hldms_dir))

        if config_hl2dm_dir:
            if (Path(config_hl2dm_dir) / "hl2.exe").exists():
                hl2dm_dir = Path(config_hl2dm_dir)
                self.ui.HL2DM_path_label.setText(str(hl2dm_dir))

        if config_dods_dir:
            if (Path(config_dods_dir) / "dod.exe").exists():
                dods_dir = Path(config_dods_dir)
                self.ui.DOD_path_label.setText(str(dods_dir))

        if config_css_dir:
            if (Path(config_css_dir) / "hl2.exe").exists():
                css_dir = Path(config_css_dir)
                self.ui.CSS_path_label.setText(str(css_dir))

        if config_csgo_dir:
            if (Path(config_csgo_dir) / "csgo.exe").exists():
                csgo_dir = Path(config_csgo_dir)
                self.ui.CSGO_path_label.setText(str(csgo_dir))

def write_config():
    config["REPO"] = {"TargetRepoTF2": target_repo_tf2,
                      "TargetRepoCSGO": target_repo_csgo,
                      "TargetRepoGeneral": target_repo_general,
                      "LastCheckedCommitSHATF2": last_checked_commit_sha_tf2,
                      "LastCheckedCommitSHACSGO": last_checked_commit_sha_csgo,
                      "LastCheckedCommitSHAGeneral": last_checked_commit_sha_general
                      # "GamesUsingRepoTF2": ",".join(games_using_tf2_repo),
                      # "GamesUsingRepoCSGO": ",".join(games_using_csgo_repo),
                      # "GamesUsingRepoGeneral": ",".join(games_using_general_repo)
                      }
    config["USER.DIRECTORIES"] = {"l4d2Dir": Path(l4d2_dir).as_posix() if l4d2_dir else "",
                                  "tf2Dir": Path(tf2_dir).as_posix() if tf2_dir else "",
                                  "hldmsDir": Path(hldms_dir).as_posix() if hldms_dir else "",
                                  "hl2dmDir": Path(hl2dm_dir).as_posix() if hl2dm_dir else "",
                                  "dodsDir": Path(dods_dir).as_posix() if dods_dir else "",
                                  "cssDir": Path(css_dir).as_posix() if css_dir else "",
                                  "csgoDir": Path(csgo_dir).as_posix() if csgo_dir else ""}

    with open("config.ini", "w") as configfile:
        config.write(configfile)

def get_game_directory(self, game):
    global l4d2_dir, tf2_dir, hldms_dir, hl2dm_dir, dods_dir, css_dir, csgo_dir
    folder = QFileDialog.getExistingDirectory(self, f"Select {game} Directory")

    if folder: # If user selected a directory
        folder = Path(folder)
        if folder.exists():
            if game == "TF2":
                if (folder / "tf.exe").exists():
                    tf2_dir = folder
                    self.ui.TF2_path_label.setText(str(folder))

            elif game == "HLDM:S":
                if (folder / "hl1mp.exe").exists():
                    hldms_dir = folder
                    self.ui.HLDMS_path_label.setText(str(folder))

            elif game == "HL2:DM":
                if (folder / "hl2.exe").exists():
                    hl2dm_dir = folder
                    self.ui.HL2DM_path_label.setText(str(folder))

            elif game == "DoD:S":
                if (folder / "dod.exe").exists():
                    dods_dir = folder
                    self.ui.DOD_path_label.setText(str(folder))

            elif game == "L4D2":
                if (folder / "left4dead2.exe").exists():
                    l4d2_dir = folder
                    self.ui.L4D2_path_label.setText(str(folder))

            elif game == "CS:GO":
                if (folder / "csgo.exe").exists():
                    csgo_dir = folder
                    self.ui.CSGO_path_label.setText(str(folder))

            elif game == "CS:S":
                if (folder / "hl2.exe").exists():
                    css_dir = folder
                    self.ui.CSS_path_label.setText(str(folder))

def get_latest_SHA(repo):
    url = f"{api_url}{repo}/commits"
    response = requests.get(url)
    if response.status_code == 200:
        commits = response.json()
        if commits:
            latest_sha = commits[0]["sha"]
            print(f"Latest Commit SHA: {latest_sha}")
            return latest_sha
        else:
            return None
    else:
        return None

def get_repo_diff(repo, last_checked_sha, latest_sha):
    if repo and last_checked_sha and latest_sha:
        url = f"{api_url}{repo}/compare/{last_checked_sha}...{latest_sha}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None
    else:
        return None

def check_for_update(repo):
    global latest_commit_sha_csgo, latest_commit_sha_general, latest_commit_sha_tf2
    global files_to_copy_fastdl_tf2, files_to_copy_fastdl_csgo, files_to_copy_fastdl_general

    if repo == target_repo_tf2:
        latest_commit_sha_tf2 = get_latest_SHA(target_repo_tf2)

        if latest_commit_sha_tf2 and latest_commit_sha_tf2 != last_checked_commit_sha_tf2:
            print("Getting TF2 Diff")
            diff = get_repo_diff(target_repo_tf2, last_checked_commit_sha_tf2, latest_commit_sha_tf2)
            if diff:
                print("diffs found")
                files = diff.get("files", "")
                if files:
                    print("diff files found")
                    for changed_file in files:
                        files_to_copy_fastdl_tf2.append(changed_file)
        elif latest_commit_sha_tf2 == last_checked_commit_sha_tf2:
            print("TF2 repo has had no changes since last sync.")
        else:
            print(f"CANT CHECK TF2 REPO DIFF\nLatest Commit: {latest_commit_sha_tf2}\n Last checked Commit: {last_checked_commit_sha_tf2}")

    elif repo == target_repo_csgo:
        latest_commit_sha_csgo = get_latest_SHA(target_repo_csgo)

        if latest_commit_sha_csgo and latest_commit_sha_csgo != last_checked_commit_sha_csgo:
            print("Getting CSGO Diff")
            diff = get_repo_diff(target_repo_csgo, last_checked_commit_sha_csgo, latest_commit_sha_csgo)
            if diff:
                files = diff.get("files", "")
                if files:
                    for changed_file in files:
                        files_to_copy_fastdl_csgo.append(changed_file)
        elif latest_commit_sha_csgo == last_checked_commit_sha_csgo:
            print("CSGO repo has had no changes since last sync.")
        else:
            print(f"CANT CHECK CSGO REPO DIFF\nLatest Commit: {latest_commit_sha_csgo}\n Last checked Commit: {last_checked_commit_sha_csgo}")

    elif repo == target_repo_general:
        latest_commit_sha_general = get_latest_SHA(target_repo_general)

        if latest_commit_sha_general and latest_commit_sha_general != last_checked_commit_sha_general:
            print("Getting General Diff")
            diff = get_repo_diff(target_repo_general, last_checked_commit_sha_general, latest_commit_sha_general)
            if diff:
                files = diff.get("files", "")
                if files:
                    for changed_file in files:
                        files_to_copy_fastdl_general.append(changed_file)
        elif latest_commit_sha_general == last_checked_commit_sha_general:
            print("General repo has had no changes since last sync.")
        else:
            print(f"CANT CHECK GENERAL REPO DIFF\nLatest Commit: {latest_commit_sha_general}\nLast checked Commit: {latest_commit_sha_general}")

def clone_repo_zip(repo):
    print("clone_repo_zip")
    url = f"{api_url}{repo}/zipball/main"
    print("sending request")

    with requests.get(url, stream=True) as response:
        print("got response")
        if response.status_code == 200:
            print("code 200")
            filename = f"{repo.replace('/', '_')}.zip"
            filepath = local_folder / filename
            if filepath.exists():
                print("REPO ZIP ALREADY DETECTED. CANCELLING DOWNLOAD TO ENSURE VALID FILE clone_repo_zip")
                return None

            downloaded = 0
            with open(filepath, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        if downloaded % (1024 * 1024) < 8192:
                            print(f"\rDownloaded {downloaded / 1024 / 1024:.2f} MB of {filename}", end="")

                print(f"\nFinished downloading {filename} ({downloaded / 1024 / 1024:.2f} MB)")
            print(f"finished downloading {filename}")

            #shutil.move((Path().absolute() / filename), local_folder)
            return True

        else:
            return None

def clone_repo(repo, game):
    print("clone_repo")
    global latest_commit_sha_csgo, latest_commit_sha_general, latest_commit_sha_tf2
    global last_checked_commit_sha_csgo, last_checked_commit_sha_general, last_checked_commit_sha_tf2

    url = f"{api_url}{repo}/zipball/main"
    print("sending request")

    with requests.get(url, stream=True) as response:
        latest_commit_sha = get_latest_SHA(repo)
        print("got response")
        if response.status_code == 200:
            print("code 200")
            filename = f"{repo.replace('/', '_')}.zip"
            filepath = local_folder / filename
            if filepath.exists():
                print("REPO ZIP ALREADY DETECTED. CANCELLING DOWNLOAD TO ENSURE VALID FILE clone_repo")
                return None

            downloaded = 0
            with open(filepath, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        if downloaded % (1024 * 1024) < 8192:
                            print(f"\rDownloaded {downloaded / 1024 / 1024:.2f} MB of {filename}", end="")

                print(f"\nFinished downloading {filename} ({downloaded / 1024 / 1024:.2f} MB)")
            print(f"finished downloading {filename}")

            #shutil.move((Path().absolute() / filename), local_folder)
            if filepath.exists():
                temp_dir = local_folder / "temp"
                if not temp_dir.exists():
                    temp_dir.mkdir(exist_ok=True)

                with ZipFile(local_folder / filename, "r") as zip:
                    zip.extractall(path=temp_dir)

                inner_root = next(temp_dir.iterdir())
                inner_path = temp_dir / inner_root.name

                for file in inner_path.iterdir():
                    shutil.move(Path(file).absolute(), local_folder)

                if (local_folder / ".gitattributes").exists():
                    (local_folder / ".gitattributes").unlink()

                if (local_folder / filename).exists():
                    (local_folder / filename).unlink()

                shutil.rmtree(temp_dir)
                # After cloning new repo, save the cloned commit to the relevant variable.
                if game == "TF2":
                    last_checked_commit_sha_tf2 = latest_commit_sha
                    latest_commit_sha_tf2 = latest_commit_sha
                elif game == "CSGO":
                    last_checked_commit_sha_csgo = latest_commit_sha
                    latest_commit_sha_csgo = latest_commit_sha
                elif game == "general":
                    last_checked_commit_sha_general = latest_commit_sha
                    latest_commit_sha_general = latest_commit_sha

                return True
            else:
                return None
        else:
            print(f"status code: {response.status_code}")
            return None

def copy_folder_to_download(dir_path: Path, fastdl: Path, download_path):
    print("copy_folder_to_download")
    if dir_path.exists() and fastdl.exists():
        downloads_folder = dir_path / download_path
        downloads_folder.mkdir(exist_ok=True)

        for folder in os.listdir(fastdl):
            source_path = fastdl / folder
            dest_path = downloads_folder / folder
            if source_path.is_dir():
                print(f"copying folder {source_path} to {dest_path}")
                shutil.copytree(source_path, dest_path, dirs_exist_ok=True)

def sync_repo():
    print("sync_repo")
    global latest_commit_sha_csgo, latest_commit_sha_general, latest_commit_sha_tf2
    global last_checked_commit_sha_csgo, last_checked_commit_sha_general, last_checked_commit_sha_tf2
    global files_to_copy_fastdl_tf2, files_to_copy_fastdl_csgo, files_to_copy_fastdl_general
    #tf2_fastdl, csgo_fastdl, general_fastdl = (local_folder / "fastdl"), (local_folder / "fastdl_csgo"), (local_folder / "fastdl_css")
    tf2_fastdl, csgo_fastdl, general_fastdl = (local_folder / "sync-testing"), (local_folder / "fastdl_csgo"), (local_folder / "fastdl_css")

    if not local_folder.exists():
        local_folder.mkdir(exist_ok=True)

    # SYNC REPOS

    # if (local_folder / tf2_fastdl).exists(): # Sync TF2 repo
    #     latest_commit_sha_tf2 = get_latest_SHA(target_repo_tf2)
    #     if latest_commit_sha_tf2 and latest_commit_sha_tf2 != last_checked_commit_sha_tf2:
    #         print("getting diff")
    #         diff = get_repo_diff(target_repo_tf2, last_checked_commit_sha_tf2, latest_commit_sha_tf2)
    #         if diff:
    #             files = diff.get("files", "")
    #             if files:
    #                 for changed_file in files:
    #                     files_to_copy_fastdl_tf2.append(changed_file)
    #     elif latest_commit_sha_tf2 == last_checked_commit_sha_tf2:
    #         print("TF2 repo has had no changes since last sync.")
    #
    # if (local_folder / csgo_fastdl).exists(): # Sync CSGO repo
    #     latest_commit_sha_csgo = get_latest_SHA(target_repo_csgo)
    #     if latest_commit_sha_csgo and latest_commit_sha_csgo != last_checked_commit_sha_csgo:
    #         diff = get_repo_diff(target_repo_csgo, last_checked_commit_sha_csgo, latest_commit_sha_csgo)
    #         if diff:
    #             files = diff.get("files", "")
    #             if files:
    #                 for changed_file in files:
    #                     files_to_copy_fastdl_csgo.append(changed_file)
    #     elif latest_commit_sha_csgo != last_checked_commit_sha_csgo:
    #         print("CSGO repo has had no changes since last sync.")
    #
    # if (local_folder / general_fastdl).exists(): # Sync general repo
    #     latest_commit_sha_general = get_latest_SHA(target_repo_general)
    #     if latest_commit_sha_general and latest_commit_sha_general != last_checked_commit_sha_general:
    #         diff = get_repo_diff(target_repo_general, last_checked_commit_sha_general, latest_commit_sha_general)
    #         if diff:
    #             files = diff.get("files", "")
    #             if files:
    #                 for changed_file in files:
    #                     files_to_copy_fastdl_general.append(changed_file)

    # Clone repos if not found and required for games
    if not (local_folder / tf2_fastdl).exists() and tf2_dir:
        clone_repo(target_repo_tf2, "TF2")
    if not (local_folder / csgo_fastdl).exists() and csgo_dir:
        clone_repo(target_repo_csgo, "CSGO")
    if not (local_folder / general_fastdl).exists() and (css_dir or l4d2_dir or dods_dir or hldms_dir or hl2dm_dir):
        clone_repo(target_repo_general, "general")

    # Copy files if diff exists

    def extract_diff_files(zip_path, file_list):
        print("extract_diff_files")
        try:
            with ZipFile(zip_path, "r") as repozip:
                # Zip file contains one folder that then contains the actual zip, this sucks
                if not repozip.namelist():
                    print(f"Error: Zip file {zip_path} is empty.")
                    return

                root_dir = repozip.namelist()[0]
                if not root_dir.endswith('/'):
                    root_dir = root_dir.split('/')[0] + '/'

                print(f"Extracting from {zip_path}, root dir: {root_dir}")

                for file_data in file_list:
                    filename = file_data.get("filename", "")
                    if not filename:
                        continue

                    zip_file_path = root_dir + filename
                    target_file_path = local_folder / filename

                    # Create parent folders if they don't exist
                    target_file_path.parent.mkdir(parents=True, exist_ok=True)

                    try:
                        # Manually read from zip and write
                        with repozip.open(zip_file_path) as source, open(target_file_path, "wb") as target:
                            print(f"  Extracting: {filename}")
                            shutil.copyfileobj(source, target)
                    except KeyError:
                        print(f"  Warning: File '{filename}' (path: '{zip_file_path}') not found in zip.")
                        print(f"Attempting to delete {filename} from local copy..")

                        if target_file_path.exists(): # If the file is not found in the zip, delete it on local
                            target_file_path.unlink()
                            print(f"SUCCESS: Deleted {target_file_path}")

                            parent_folder = target_file_path.parent
                            if parent_folder.exists(): # Delete parent folder if it is empty
                                if not any(parent_folder.iterdir()):
                                    parent_folder.rmdir()

                    except Exception as e:
                        print(f"  Error extracting {filename}: {e}")

        except FileNotFoundError:
            print(f"Error: Zip file {zip_path} not found.")
        except Exception as e:
            print(f"Error opening zip {zip_path}: {e}")
        finally:
            if zip_path.exists():
                zip_path.unlink()
                print(f"Cleaned up {zip_path}")

    # Extract files from zip if diff found
    if files_to_copy_fastdl_general:
        clone_repo_zip(target_repo_general)
        zip_filename = f"{target_repo_general.replace('/', '_')}.zip"
        zip_filepath = local_folder / zip_filename
        if zip_filepath.exists():
            extract_diff_files(zip_filepath, files_to_copy_fastdl_general)
            last_checked_commit_sha_general = latest_commit_sha_general

    if files_to_copy_fastdl_csgo:
        clone_repo_zip(target_repo_csgo)
        zip_filename = f"{target_repo_csgo.replace('/', '_')}.zip"
        zip_filepath = local_folder / zip_filename
        if zip_filepath.exists():
            extract_diff_files(zip_filepath, files_to_copy_fastdl_csgo)
            last_checked_commit_sha_csgo = latest_commit_sha_csgo

    if files_to_copy_fastdl_tf2:
        print("files_to_copy_fastdl_tf2")
        clone_repo_zip(target_repo_tf2)
        zip_filename = f"{target_repo_tf2.replace('/', '_')}.zip"
        zip_filepath = local_folder / zip_filename
        if zip_filepath.exists():
            extract_diff_files(zip_filepath, files_to_copy_fastdl_tf2)
            last_checked_commit_sha_tf2 = latest_commit_sha_tf2

    print("Sync Complete, copying files to required directories..")

    if Path(tf2_dir).exists():
        copy_folder_to_download(Path(tf2_dir), tf2_fastdl, "tf/download")
    if Path(csgo_dir).exists():
        copy_folder_to_download(Path(csgo_dir), csgo_fastdl, "csgo")
    if Path(l4d2_dir).exists():
        copy_folder_to_download(Path(l4d2_dir), general_fastdl, "left4dead2")
    if Path(css_dir).exists():
        copy_folder_to_download(Path(css_dir), general_fastdl, "cstrike/download")
    if Path(hldms_dir).exists():
        copy_folder_to_download(Path(hldms_dir), general_fastdl, "hl1mp/download")
    if Path(hl2dm_dir).exists():
        copy_folder_to_download(Path(hl2dm_dir), general_fastdl, "hl2mp/download")
    if Path(dods_dir).exists():
        copy_folder_to_download(Path(dods_dir), general_fastdl, "dod/download")

    files_to_copy_fastdl_tf2.clear()
    files_to_copy_fastdl_csgo.clear()
    files_to_copy_fastdl_general.clear()

check_for_update(target_repo_csgo)
check_for_update(target_repo_general)
check_for_update(target_repo_tf2)
sync_repo()