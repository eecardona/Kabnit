import sys

from PyQt6.QtCore import (
    QAbstractAnimation,
    QParallelAnimationGroup,
    QPropertyAnimation,
    Qt,
    pyqtSignal,
)
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLayout,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

COLLAPSED_WIDTH = 40                      # width of the menu column when closed
PANEL_WIDTH = 180                         # extra width added when open
EXPANDED_WIDTH = COLLAPSED_WIDTH + PANEL_WIDTH
ANIMATION_DURATION = 250                  # milliseconds
MENU_ITEMS = ["Home", "Projects", "Settings", "Help"]


class SideMenu(QFrame):
    item_clicked = pyqtSignal(str)        # emits the text of the clicked menu item

    def __init__(self, animation_duration: int = ANIMATION_DURATION, parent=None):
        super().__init__(parent)
        self.animation_duration = animation_duration
        self.setStyleSheet(
            "QToolButton { border: none; font-size: 18px; }"
            "QPushButton { background: transparent; border: none; text-align: left; "
            "padding: 6px 12px; }"
            "QPushButton:hover { color: #4a90d9; }"
        )

        # Header row: the menu icon, aligned to the right edge of the column
        self.toggle_button = QToolButton()
        self.toggle_button.setText("\u2630")  # hamburger icon (☰)
        self.toggle_button.setToolTip("Toggle menu")
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        self.toggle_button.setFixedSize(COLLAPSED_WIDTH, COLLAPSED_WIDTH)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)
        header_layout.addStretch()
        header_layout.addWidget(self.toggle_button, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        header = QWidget()
        header.setLayout(header_layout)

        # Menu items: stacked below the icon in the same column, text left-aligned
        self.items_container = QWidget()
        self.items_container.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred
        )

        items_layout = QVBoxLayout()
        items_layout.setContentsMargins(0, 4, 0, 0)
        items_layout.setSpacing(2)
        for text in MENU_ITEMS:
            item = QPushButton(text)
            item.setFlat(True)
            item.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
            # 'name=text' freezes the current item name inside each lambda
            item.clicked.connect(lambda checked=False, name=text: self.item_clicked.emit(name))
            items_layout.addWidget(item)
        items_layout.addStretch()
        self.items_container.setLayout(items_layout)

        # Hidden while collapsed so nothing shows below the icon
        self.items_container.hide()

        # The whole menu is one vertical column; its width is what animates
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        root_layout.addWidget(header)
        root_layout.addWidget(self.items_container, 1)
        self.setLayout(root_layout)

        # Start collapsed
        self.setMinimumWidth(COLLAPSED_WIDTH)
        self.setMaximumWidth(COLLAPSED_WIDTH)

        # Animate minimum and maximum width from collapsed to expanded
        self.min_width_animation = QPropertyAnimation(self, b"minimumWidth")
        self.max_width_animation = QPropertyAnimation(self, b"maximumWidth")
        for animation in (self.min_width_animation, self.max_width_animation):
            animation.setDuration(self.animation_duration)
            animation.setStartValue(COLLAPSED_WIDTH)
            animation.setEndValue(EXPANDED_WIDTH)

        self.toggle_animation = QParallelAnimationGroup()
        self.toggle_animation.addAnimation(self.min_width_animation)
        self.toggle_animation.addAnimation(self.max_width_animation)
        self.toggle_animation.finished.connect(self._on_animation_finished)

        self.toggle_button.clicked.connect(self._on_toggle_clicked)

    def _on_toggle_clicked(self, checked: bool):
        if checked:
            # Show the items before the menu opens so they slide out with it
            self.items_container.show()

        direction = (
            QAbstractAnimation.Direction.Forward
            if checked
            else QAbstractAnimation.Direction.Backward
        )
        self.toggle_animation.setDirection(direction)
        # Reverses smoothly if the menu is already animating
        if self.toggle_animation.state() != QAbstractAnimation.State.Running:
            self.toggle_animation.start()

    def _on_animation_finished(self):
        # Once the menu has fully closed, hide the items again
        if not self.toggle_button.isChecked():
            self.items_container.hide()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Side Menu Example")
        self.resize(800, 500)

        central = QWidget()
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.side_menu = SideMenu()
        self.side_menu.item_clicked.connect(self.handle_menu_item)
        root_layout.addWidget(self.side_menu)

        self.status_label = QLabel("Click the menu icon in the top left to open the menu.")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root_layout.addWidget(self.status_label, 1)

        self.setCentralWidget(central)

    def handle_menu_item(self, name: str):
        # PLACEHOLDER: replace this with your real functions.
        # For example: if name == "Settings": self.open_settings()
        self.status_label.setText(f"Placeholder: '{name}' was clicked.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
