import sys

import gui
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    dialog = gui.LoginDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        username, password = dialog.credentials()
        # Submit credentials securely; don't log or save the password.
        dialog.password_input.clear()

    sys.exit(0)
