from PyQt6.QtWidgets import QFileDialog
from pathlib import Path

def get_game_directory(self, ui, game):
    folder = QFileDialog.getExistingDirectory(self, "Select Folder")
