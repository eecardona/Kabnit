from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QPalette
from bloolib import check_user, ensure_db, postgres_check
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

app = QApplication(sys.argv)

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
    os.environ["QT_QPA_PLATFORMTHEME"] = "kde"  # Plan to change this to a sys call to identify user session and set theme for them.

    if not postgres_check():
        print("Check returned False")
        gui.warning_postgres()
    else:
        check_user()
        if not ensure_db():
            sys.exit(1)


    font_id = QFontDatabase.addApplicationFont(str(config.BASE_DIR / "static" / "fonts" / "DEMO Broncks.ttf"))
    if font_id <0:
        logger.error("ERROR: Failed to load font")
    else:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

    window = gui.MainWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()
