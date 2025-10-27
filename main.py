import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QThread, QTimer
from gui import Ui_MainWindow
import resources
import logic
import atexit

class LogicThread(QThread):
    def __init__(self):
        super().__init__()

    def run(self):
        logic.sync_repo()


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
        self.ui.download_button.clicked.connect(self.on_download_press)

        # logic.check_for_update(logic.target_repo_tf2)
        # logic.check_for_update(logic.target_repo_csgo)
        # logic.check_for_update(logic.target_repo_general)
        updated_repos = []
        if logic.files_to_copy_fastdl_tf2:
            updated_repos.append("TF2")
        if logic.files_to_copy_fastdl_csgo:
            updated_repos.append("CS:GO")
        if logic.files_to_copy_fastdl_general:
            updated_repos.append("Other")

        update_button_text = ""
        for repo in updated_repos:
            if not repo == updated_repos[-1]:
                update_button_text = update_button_text + repo + ", "
            else:
                update_button_text = update_button_text + repo

        if update_button_text:
            self.ui.download_button.setText("Download Updates: " + update_button_text)
        else:
            self.ui.download_button.setText("Download FastDL Content (No Updates)")
        self.ui.download_button.setEnabled(True)
        self.thread = LogicThread()

    def on_download_press(self):
        self.ui.download_button.setDisabled(True)
        self.ui.download_button.setText("Syncing.. Check Command Window for Progress")

        ui = self.ui
        dir_buttons = [ui.TF2_set_dir_button, ui.HLDMS_set_dir_button, ui.HL2DM_set_dir_button, ui.DOD_set_dir_button,
                       ui.L4D2_set_dir_button, ui.CSS_set_dir_button, ui.CSGO_set_dir_button]

        for button in dir_buttons:
            button.setDisabled(True)
        self.thread.start()
        self.thread.finished.connect(self.on_sync_finished)

    def on_sync_finished(self):
        self.ui.download_button.setEnabled(True)
        self.ui.download_button.setText("Sync Complete!")
        QTimer.singleShot(3000, self.reset_download_text)
    def reset_download_text(self):
        self.ui.download_button.setText("Download FastDL Content (No Updates)")

        ui = self.ui
        dir_buttons = [ui.TF2_set_dir_button, ui.HLDMS_set_dir_button, ui.HL2DM_set_dir_button, ui.DOD_set_dir_button,
                       ui.L4D2_set_dir_button, ui.CSS_set_dir_button, ui.CSGO_set_dir_button]

        for button in dir_buttons:
            button.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    app.setStyleSheet("""
        QToolTip { 
            background-color: black; 
            color: white; 
            border: 1px solid white;
            font: 12pt "VCR OSD Mono";
        }
    """)
    window.show()
    atexit.register(logic.write_config)
    sys.exit(app.exec())
