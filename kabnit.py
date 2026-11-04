from PyQt6.QtWidgets import QApplication
from datetime import datetime
import logging
import config
import bloolib
import gui
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='kabnit.log'
)
logger = logging.getLogger(__name__)

app = QApplication(sys.argv)

def main():
    if config.USERNAME == None:
        print("Welcome to KabNit! Please enter a username to identify you:")
        username = input()
        bloolib.config_update("USERNAME",f"{username}")
        config.USERNAME = username
        logger.info(f"User {username} saved as owner")
        print(f"Thanks {username}")
    if config.DB_NAME == None:
        time = datetime.now().strftime("%Y%m%d%H%M")
        db_update = (f'{config.USERNAME}{time}').lower()
        config.DB_NAME = db_update
        bloolib.config_update("DB_NAME", f"{db_update}")
        logger.info("New DB_NAME set")
        bloolib.create_db()
        bloolib.create_table()

    window = gui.MainWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()
