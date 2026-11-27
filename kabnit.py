from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QPalette
from bloolib import set_user
from pathlib import Path
import logging
import config
import gui
import sys
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='kabnit.log'
)
logger = logging.getLogger(__name__)
os.environ["QT_QPA_PLATFORMTHEME"] = "kde"  # Plan to change this to a sys call to identify user session and set theme for them.

app = QApplication(sys.argv)

icon_path = os.path.join
#Style
btn_color = app.palette().color(QPalette.ColorRole.Button)

hover_color = btn_color.darker(100)
pressed_color = btn_color.darker(150)

app.setStyleSheet(f"""
    QPushButton:hover {{
        background-color: {hover_color.name()};
    }}
    QPushButton:pressed {{
        background-color: {pressed_color.name()};
    }}
""")

def main():
    font_id = QFontDatabase.addApplicationFont(str(config.BASE_DIR / "static" / "fonts" / "Smoov.ttf"))
    if font_id <0:
        logger.error("ERROR: Failed to load font")
    else:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

    if not Path(".env").is_file():
        set_user()
        login_window = gui.LoginDialog()
        main_window = None

        def open_main_window():
            nonlocal main_window
            main_window = gui.MainWindow()
            main_window.show()
            login_window.close()

        login_window.login_successful.connect(open_main_window)
        login_window.show()

    else:
        main_window = gui.MainWindow()
        main_window.show()

    app.exec()





if __name__ == "__main__":
    main()
