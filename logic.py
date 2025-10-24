from http.client import responses
from os import mkdir

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QFileDialog
from pathlib import Path
from typing import TYPE_CHECKING
from PyQt6.QtGui import QFont, QFontMetrics
import configparser
import requests
if TYPE_CHECKING:
    from main import MainWindow

config = configparser.ConfigParser()
config.optionxform = str
default_target_repo = "dilbertron2/crossroads-FastDL-Sync-Testing"
target_repo = "dilbertron2/crossroads-FastDL-Sync-Testing"
target_branch = "master"
target_folders = ["fastdl", "fastdl-css", "fastdl-csgo"]
latest_commit_sha = ""
last_checked_commit_sha = ""
local_folder = ""
api_url = f"https://api.github.com/repos/{target_repo}"
l4d2_dir = ""
tf2_dir = ""
hldms_dir = ""
hl2dm_dir = ""
dods_dir = ""
css_dir = ""
csgo_dir = ""


#TODO read/write individual fastdl repos and what repos each game is for into the ini file
def read_config(self):
    global l4d2_dir, tf2_dir, hldms_dir, hl2dm_dir, dods_dir, target_repo, css_dir, csgo_dir

    if Path("config.ini").exists():
        config.read("config.ini")
        user_dirs = "USER.DIRECTORIES"
        repo_info = "REPO"
        config_target_repo = config[repo_info].get("TargetRepo", "")
        config_last_commit_sha = config[repo_info].get("LastCheckedCommitSHA", "")
        config_l4d2_dir = config[user_dirs].get("l4d2Dir", "")
        config_tf2_dir = config[user_dirs].get("tf2Dir", "")
        config_hldms_dir = config[user_dirs].get("hldmsDir", "")
        config_hl2dm_dir = config[user_dirs].get("hl2dmDir", "")
        config_dods_dir = config[user_dirs].get("dodsDir", "")
        config_css_dir = config[user_dirs].get("cssDir", "")
        config_csgo_dir = config[user_dirs].get("csgoDir", "")

        if config_target_repo:
            target_repo = config_target_repo

        if config_last_commit_sha:
            last_checked_commit_sha = config_last_commit_sha

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
    config["REPO"] = {"TargetRepo": target_repo,
                      "LastCheckedCommitSHA": last_checked_commit_sha}
    config["USER.DIRECTORIES"] = {"l4d2Dir": l4d2_dir,
                                  "tf2Dir": tf2_dir,
                                  "hldmsDir": hldms_dir,
                                  "hl2dmDir": hl2dm_dir,
                                  "dodsDir": dods_dir,
                                  "cssDir": css_dir,
                                  "csgoDir": csgo_dir}

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

def get_latest_commit_sha():
    url = f"{api_url}/commits/{target_branch}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()["sha"]

def get_changed_files(last_sha, latest_sha):
    url = f"{api_url}/compare/{last_sha}...{latest_sha}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data["files"]  # Each file dict contains 'filename', 'status', 'raw_url', etc.

def is_file_fastdl(file):
    filepath = file.get("raw_url", "")
    if filepath:
        print(filepath)

def sync_repo():
    global latest_commit_sha, last_checked_commit_sha

    fastdl_folder = Path().absolute() / "fastdl_content"
    if not fastdl_folder.exists():
        fastdl_folder.mkdir(exist_ok=True)

    if last_checked_commit_sha: # Update Repo
        latest_commit_sha = get_latest_commit_sha()
        changed_files = get_changed_files(last_checked_commit_sha, latest_commit_sha)

    elif not last_checked_commit_sha: # Download Repo
        pass
