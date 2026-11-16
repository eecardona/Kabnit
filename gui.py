from pathlib import Path
import logging

from PyQt6.QtWidgets import (QMainWindow, QWidget, QPushButton, QTableView, QVBoxLayout,
                             QHBoxLayout, QFormLayout, QLineEdit, QLabel, QApplication,
                             QMessageBox, QFrame, QToolButton,
                             QStackedWidget,)
from PyQt6.QtCore import (Qt, QAbstractTableModel, QAbstractAnimation, QParallelAnimationGroup,
                             QPropertyAnimation, QEvent, pyqtSignal)
from PyQt6.QtGui import QFont, QFontDatabase, QPixmap, QPalette

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


# Collapsible menu
class CollapsibleMenu(QFrame):
    add_items = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sideMenu")
        self.setAutoFillBackground(True)
        self.apply_theme_background()

        self.stack = QStackedWidget()
        self.stack.setFrameShape(QFrame.Shape.NoFrame)
        self.table_view = QTableView()
        self.table_view.setFrameShape(QFrame.Shape.NoFrame)
        self.stack.addWidget(self.table_view)

        self.setStyleSheet(
            "QToolButton { border: none; font-size: 18px; }"
            "QPushButton { background: transparent; border: none; text-align: left; "
            "padding: 6px 12px; }"
            "QPushButton:hover { color: #4a90d9; }"
            'QLabel[role="h2"] { font-size: 16px; font-weight: bold; padding: 8px 12px 4px 12px; }'
        )


        self.toggle_button = QToolButton()
        self.toggle_button.setText("\u2630")
        self.toggle_button.setCheckable(True)
        self.toggle_button.setFixedSize(config.COLLAPSED_WIDTH, config.COLLAPSED_WIDTH)

        self.menu = QVBoxLayout()
        self.menu.setContentsMargins(0, 0, 0, 0)
        self.menu.setSpacing(0)

        # Start of menu
        self.menu.actions_header = QLabel("Actions")
        self.menu.actions_header.setProperty("role", "h2")
        self.menu.addWidget(self.menu.actions_header)

        self.menu.pull_button = QPushButton("Pull Inventory")
        self.menu.pull_button.clicked.connect(self.on_pull_inventory)
        self.menu.addWidget(self.menu.pull_button)

        self.menu.add_items_button = QPushButton("Add Items")
        self.menu.add_items_button.clicked.connect(self.on_add_items)
        self.menu.addWidget(self.menu.add_items_button)

        self.menu.locations_header = QLabel("Locations")
        self.menu.locations_header.setProperty("role", "h2")
        self.menu.addWidget(self.menu.locations_header)

        self.location_buttons = {}

        locations = bloolib.load_locations()
        for location in locations:
            button = QPushButton(location)
            button.clicked.connect(lambda check=False, n=location: self.load_location_inventory(n))
            self.menu.addWidget(button)
            self.location_buttons[location] = button

        self.menu.addStretch()
        # End of menu

        self.menu_container = QWidget()
        self.menu_container.setLayout(self.menu)
        self.menu_container.hide()

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(0)
        header.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        header.addWidget(self.toggle_button)


        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addLayout(header)
        root.addWidget(self.menu_container)

        self.setMinimumWidth(config.COLLAPSED_WIDTH)
        self.setMaximumWidth(config.COLLAPSED_WIDTH)

        self.min_width_animation = QPropertyAnimation(self, b"minimumWidth")
        self.max_width_animation = QPropertyAnimation(self, b"maximumWidth")
        for animation in (self.min_width_animation, self.max_width_animation):
            animation.setDuration(config.ANIMATION_DURATION)
            animation.setStartValue(config.COLLAPSED_WIDTH)
            animation.setEndValue(config.EXPANDED_WIDTH)

        self.toggle_animation = QParallelAnimationGroup()
        self.toggle_animation.addAnimation(self.min_width_animation)
        self.toggle_animation.addAnimation(self.max_width_animation)
        self.toggle_animation.finished.connect(self._on_animation_finished)

        self.toggle_button.clicked.connect(self._on_toggle_clicked)

    def apply_theme_background(self):
        base = QApplication.palette().color(QPalette.ColorRole.Window)
        target = base.darker(config.THEME_1_BACKGROUND_DARKEN_FACT0R)
        if self.palette().color(QPalette.ColorRole.Window) != target:
            palette = QPalette(QApplication.palette())
            palette.setColor(QPalette.ColorRole.Window, target)
            self.setPalette(palette)


    def changeEvent(self, event):
        if event.type() in (QEvent.Type.PaletteChange, QEvent.Type.StyleChange):
            self.apply_theme_background()
        super().changeEvent(event)

    def _on_toggle_clicked(self, checked: bool):
        if checked:
            self.menu_container.show()
        direction = (
            QAbstractAnimation.Direction.Forward
            if checked
            else QAbstractAnimation.Direction.Backward
        )
        self.toggle_animation.setDirection(direction)
        if self.toggle_animation.state() != QAbstractAnimation.State.Running:
            self.toggle_animation.start()

    def _on_animation_finished(self):
        if not self.toggle_button.isChecked():
            self.menu_container.hide()

    def display_inventory(self, rows, headers):
        try:
            self.table_model = PostgresTableModel(rows, headers)
            self.table_view.setModel(self.table_model)
            self.stack.setCurrentWidget(self.table_view)
            logger.info("Inventory pulled successfully")
        except Exception as e:
            logger.error(f"Error pulling inventory: {e}")
            print(f"Error: {e}")

    def on_pull_inventory(self):
        rows, headers = bloolib.pull_inventory()
        self.display_inventory(rows, headers)

    def on_add_items(self):
        self.add_items.emit()

    def load_location_inventory(self, location):
        rows, headers = bloolib.pull_location(location)
        self.display_inventory(rows, headers)





def build_menu_layout(parent_layout: QVBoxLayout):
    row = QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(0)

    side_menu = CollapsibleMenu()

    central = QVBoxLayout()
    central.addWidget(side_menu.stack)


    row.addWidget(side_menu)
    row.addLayout(central, 1)
    parent_layout.addLayout(row)

    return side_menu, central

# I am not sure how this works. but it works.
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
    search = pyqtSignal
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
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title bar Contents
        title_bar = QHBoxLayout()
        darker = QApplication.palette().color(QPalette.ColorRole.Window).darker(config.THEME_2_BACKGROUND_DARKEN_FACT0R)


        self.logo = QLabel()
        self.logo.setContentsMargins(-4, 0, 0, 0)
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
        self.search_bar.returnPressed.connect(self.do_search)
        title_bar.addWidget(self.search_bar)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.do_search)
        title_bar.addWidget(self.search_button)

        title_widget = QWidget()
        title_widget.setAutoFillBackground(True)
        palette = title_widget.palette()
        palette.setColor(QPalette.ColorRole.Window, darker)
        title_widget.setPalette(palette)
        title_widget.setLayout(title_bar)
        layout.addWidget(title_widget)

        # Split menu window
        self.side_menu, self.central = build_menu_layout(layout)
        self.side_menu.add_items.connect(self.open_add_items_form)

        central_widget.setLayout(layout)

    def do_search(self):
        text = self.search_bar.text().strip()
        if not text:
            return
        rows, headers = bloolib.search(text)
        self.side_menu.display_inventory(rows, headers)

    def on_pull_inventory(self):
        rows, headers = bloolib.pull_inventory()
        self.display_inventory(rows, headers)

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
