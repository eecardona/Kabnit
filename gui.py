from PyQt6.QtWidgets import QMainWindow, QWidget, QPushButton, QTableView, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit
from PyQt6.QtCore import Qt, QAbstractTableModel, pyqtSignal
import PyQt6.QtGui
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

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

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


    def on_pull_inventory(self):
        try:
            rows, headers = bloolib.pull_inventory()
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
        self.setWindowTitle("Add Items Form")

        self.form_layout = QFormLayout()
        self.setLayout(self.form_layout)

        for i in range(3):
            self.add_row()

        self.add_button = QPushButton("Add Row")
        self.add_button.clicked.connect(self.add_row)
        self.form_layout.addWidget(self.add_button)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.on_submit_form)
        self.form_layout.addWidget(self.submit_button)


        self.back_button = QPushButton("Cancel")
        self.back_button.clicked.connect(self.cancel)
        self.form_layout.addWidget(self.back_button)

    def add_row(self):
        hbox = QHBoxLayout()
        fields = []
        for placeholder in ["Item name", "Brand name", "Amount", "Units", "Location", "Expiration date", "Price paid"]:
            line = QLineEdit()
            line.setPlaceholderText(placeholder)
            fields.append(line)
            hbox.addWidget(line)
        self.rows.append(fields)
        self.form_layout.insertRow(self.form_layout.count() - 3, hbox)

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
        rows = self.submit()

        if bloolib.insert_form_data(rows):
            logger.info("Data inserted successfully!")
            self.closed.emit()
            self.close()
        else:
            print("Data insert failed")

    def cancel(self):
        self.closed.emit()
        self.close()
