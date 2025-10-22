import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from gui import Ui_MainWindow
import logic


# def on_dir_button_clicked(game):
#     logic.get_game_directory(game)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        logic.read_config(self)

        # Connect directory buttons to handler
        self.ui.TF2_set_dir_button.clicked.connect(lambda: logic.get_game_directory(self, "TF2"))
        self.ui.HLDMS_set_dir_button.clicked.connect(lambda: logic.get_game_directory(self, "HLDM:S"))
        self.ui.HL2DM_set_dir_button.clicked.connect(lambda: logic.get_game_directory(self, "HL2:DM"))
        self.ui.DOD_set_dir_button.clicked.connect(lambda: logic.get_game_directory(self, "DoD:S"))
        self.ui.L4D2_set_dir_button.clicked.connect(lambda: logic.get_game_directory(self, "L4D2"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
