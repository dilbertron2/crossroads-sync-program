import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow
from gui import Ui_MainWindow
import logic
import atexit


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.resize(1000, 600)

        logic.read_config(self)

        # Connect directory buttons to handler
        self.ui.TF2_set_dir_button.clicked.connect(lambda: logic.get_game_directory(self, "TF2"))
        self.ui.HLDMS_set_dir_button.clicked.connect(lambda: logic.get_game_directory(self, "HLDM:S"))
        self.ui.HL2DM_set_dir_button.clicked.connect(lambda: logic.get_game_directory(self, "HL2:DM"))
        self.ui.DOD_set_dir_button.clicked.connect(lambda: logic.get_game_directory(self, "DoD:S"))
        self.ui.L4D2_set_dir_button.clicked.connect(lambda: logic.get_game_directory(self, "L4D2"))
        self.ui.CSS_set_dir_button.clicked.connect(lambda: logic.get_game_directory(self, "CS:S"))
        self.ui.CSGO_set_dir_button.clicked.connect(lambda: logic.get_game_directory(self, "CS:GO"))
        self.ui.download_button.clicked.connect(logic.sync_repo)

atexit.register(logic.write_config)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
