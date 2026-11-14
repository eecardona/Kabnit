from pathlib import Path
import logging

from PyQt6.QtWidgets import (QMainWindow, QWidget, QPushButton, QTableView, QVBoxLayout,
                             QHBoxLayout, QFormLayout, QLineEdit, QLabel, QTableWidget,
                             QMessageBox, QTableWidgetItem)
from PyQt6.QtCore import Qt, QAbstractTableModel, pyqtSignal
from PyQt6.QtGui import QFont, QFontDatabase, QPixmap
from ctypes import alignment

import bloolib
import config

logger = logging.getLogger(__name__)

# Install and warning windows
def warning_postgres():
    app = QWidget()
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Warning)
    msg_box.setText("The PostgreSQL server is not running.")
    msg_box.setInformativeText("Do you want to start it?")
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
    msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
    response = msg_box.exec()

    if response == QMessageBox.StandardButton.Ok:
        bloolib.start_postgres_server()
    else:
        app.quit()




class PostgresTableModel(QAbstractTableModel):
    def __init__(self, data, headers):
        super().__init__()
        self.data_rows = data
        self.headers = headers

    def rowCount(self, parent=None):
        return len(self.data_rows)

    def columnCount(self, parent=None):
        return len(self.headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return self.data_rows[index.row()][index.column()]
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KabNit: Self-Hosted Inventory Management")
        self.setGeometry(100, 100, 800, 600)

        font_id = QFontDatabase.applicationFontFamilies(
            QFontDatabase.addApplicationFont(str(config.BASE_DIR / "static" / "fonts" / "DEMO Broncks.ttf"))
        )

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # Title bar Contents
        title_bar = QHBoxLayout()

        self.logo = QLabel()
        pixmap = QPixmap(str(config.BASE_DIR / "static" / "logo.png"))
        self.logo.setPixmap(pixmap.scaledToHeight(32, Qt.TransformationMode.SmoothTransformation))
        title_bar.addWidget(self.logo)

        self.app_name = QLabel("KabNit")
        self.app_name.setFixedHeight(46)
        self.app_name.setContentsMargins(0, 8, 0, 0)
        self.app_name.setFont(QFont("Broncks DEMO", 28, QFont.Weight.Bold))
        self.app_name.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
        title_bar.addWidget(self.app_name)

        title_bar.addStretch()

        self.greeting = QLabel(f"Hello, {config.USERNAME}")
        self.greeting.setFixedHeight(46)
        self.greeting.setFont(QFont("Sans Serif", 14, QFont.Weight.Bold))
        self.greeting.setContentsMargins(0, 8, 0, 0)
        title_bar.addWidget(self.greeting)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search by item name")
        title_bar.addWidget(self.search_bar)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.do_search)
        title_bar.addWidget(self.search_button)

        layout.addLayout(title_bar)

        self.pull_button = QPushButton("Pull Inventory")
        self.pull_button.clicked.connect(self.on_pull_inventory)
        layout.addWidget(self.pull_button)

        self.table_view = QTableView()
        layout.addWidget(self.table_view)

        self.add_items = QPushButton("Add Items")
        self.add_items.clicked.connect(self.open_add_items_form)
        self.add_form = None
        layout.addWidget(self.add_items)

        central_widget.setLayout(layout)

    def do_search(self):
        text = self.search_bar.text().strip()
        if not text:
            return
        rows, headers = bloolib.search(text)
        self.display_inventory(rows, headers)

    def on_pull_inventory(self):
        try:
            rows, headers = bloolib.pull_inventory()
            model = PostgresTableModel(rows, headers)
            self.table_view.setModel(model)
            logger.info("Inventory pulled successfully")
        except Exception as e:
            logger.error(f"Error pulling inventory: {e}")
            print(f"Error: {e}")

    def display_inventory(self, rows, headers):
        try:
            model = PostgresTableModel(rows, headers)
            self.table_view.setModel(model)
            logger.info("Inventory pulled successfully")
        except Exception as e:
            logger.error(f"Error pulling inventory: {e}")
            print(f"Error: {e}")

    def open_add_items_form(self):
        self.add_form = addItemsForm()
        self.add_form.closed.connect(self.on_form_closed)
        self. add_form.show()

    def on_form_closed(self):
        self.add_form = None
        self.show()




class addItemsForm(QWidget):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.rows = []
        self.row_layouts = []
        self.setWindowTitle("Add Items Form")

        self.form_layout = QFormLayout()
        self.setLayout(self.form_layout)

        self.add_display = QLabel("Add Item Details below")
        self.add_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.form_layout.addWidget(self.add_display)

        self.button_row()
        self.add_row()

    def add_row(self):
        hbox = QHBoxLayout()
        fields = []
        for placeholder in ["Item name", "Brand name", "Amount", "Units", "Location", "Expiration date", "Price paid"]:
            line = QLineEdit()
            line.setPlaceholderText(placeholder)
            fields.append(line)
            hbox.addWidget(line)
        self.form_layout.insertRow(self.form_layout.count() - 1, hbox)
        self.rows.append(fields)
        self.row_layouts.append(hbox)

    def remove_row(self):
        if not self.rows:
            return

        fields = self.rows.pop()
        hbox = self.row_layouts.pop()

        for widget in fields:
            hbox.removeWidget(widget)
            widget.hide()
            widget.deleteLater()

        self.form_layout.removeRow(hbox)

    # Not really sure if this is the best way to do this but its similar to form rows solution and keeps it contained idk.
    def button_row(self):
        bbox = QHBoxLayout()
        bbox.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.remove_button = QPushButton("Remove Row")
        self.remove_button.clicked.connect(lambda: self.remove_row())
        bbox.addWidget(self.remove_button)

        self.add_button = QPushButton("Add Row")
        self.add_button.clicked.connect(self.add_row)
        bbox.addWidget(self.add_button)

        self.back_button = QPushButton("Cancel")
        self.back_button.clicked.connect(self.cancel)
        bbox.addWidget(self.back_button)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.on_submit_form)
        bbox.addWidget(self.submit_button)

        self.form_layout.addRow(bbox)

    def submit(self):
        rows = []
        for row in self.rows:
            rows.append((
                row[0].text(), #Item name
                row[1].text() or None, #Brand name
                row[2].text(), #Amount
                row[3].text(), #Units
                row[4].text(), #Location
                None,         #Barcode
                row[5].text() or None, #Expiration date
                row[6].text() or None #Price paid
            ))
        return rows

    def on_submit_form(self):
        valid = True
        for row in self.rows:
            if not row[0].text() or not row[2].text() or not row[3].text():
                QMessageBox.warning(self, "Validation Error", "All required fields must be filled.")
                valid = False
                break
        if valid:
            rows = self.submit()
            if bloolib.insert_form_data(rows):
                    logger.info("Data inserted successfully!")
                    self.closed.emit()
                    self.close()
        else:
            QMessageBox.warning(self, "Database Error", "Failed to insert data.")
            logger.error("Database error, Failed to insert data")

    def cancel(self):
        self.closed.emit()
        self.close()
