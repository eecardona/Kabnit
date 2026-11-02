from PyQt6.QtWidgets import QMainWindow, QWidget, QPushButton, QTableView, QVBoxLayout
from PyQt6.QtCore import Qt, QAbstractTableModel
import logging
import bloolib

logger = logging.getLogger(__name__)

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
        if role == Qt.ItemDataRole.DisplayRole and orienation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KabNit")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        self.pull_button = QPushButton("Pull Inventory")
        self.pull_button.clicked.connect(self.on_pull_inventory)
        layout.addWidget(self.pull_button)

        self.table_view = QTableView()
        layout.addWidget(self.table_view)

        central_widget.setLayout(layout)

    def on_pull_inventory(self):
        try:
            rows, headers = bloolib.pull_inventory()
            model = PostgresTableModel(rows, headers)
            self.table_view.setModel(model)
            logger.info("Inventory pulled successfully")
        except Exception as e:
            logger.error(f"Error pulling inventory: {e}")
            print(f"Error: {e}")

    def on_submit_form(self):
        rows = self.get_form_data()

        if bloolib.insert_form_data(rows):
            logger.info("Data inserted successfully!")
            self.clear_form()
        else:
            print("Insert Failed")

    def clear_form():
        return "not done yet brother"
