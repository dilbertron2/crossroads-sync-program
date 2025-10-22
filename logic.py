from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QFileDialog
from pathlib import Path
from typing import TYPE_CHECKING
from PyQt6.QtGui import QFont, QFontMetrics
import configparser
if TYPE_CHECKING:
    from main import MainWindow

l4d2_dir = None
tf2_dir = None
hldms_dir = None
hl2dm_dir = None
dods_dir = None

def read_config(self):
    global l4d2_dir, tf2_dir, hldms_dir, hl2dm_dir, dods_dir
    config = configparser.ConfigParser()

    if Path("config.ini").exists():
        config.read("config.ini")
        print(config.sections())
        user_dirs = "USER.DIRECTORIES"

        config_l4d2_dir = config[user_dirs].get("l4d2_dir", "")
        if config_l4d2_dir:
            l4d2_dir = config_l4d2_dir

def get_game_directory(self, game):
    folder = QFileDialog.getExistingDirectory(self, f"Select {game} Directory")

    if folder: # If user selected a directory
        folder = Path(folder)
        if folder.exists():
            if game == "TF2":
                if (folder / "tf.exe").exists():
                    self.ui.TF2_path_label.setText(str(folder))

            elif game == "HLDM:S":
                if (folder / "hl1mp.exe").exists():
                    self.ui.HLDMS_path_label.setText(str(folder))

            elif game == "HL2:DM":
                if (folder / "hl2.exe").exists():
                    self.ui.HL2DM_path_label.setText(str(folder))

            elif game == "DoD:S":
                if (folder / "dod.exe").exists():
                    self.ui.DOD_path_label.setText(str(folder))

            elif game == "L4D2":
                if (folder / "left4dead2.exe").exists():
                    self.ui.L4D2_path_label.setText(str(folder))