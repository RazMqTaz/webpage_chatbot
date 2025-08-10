from PySide6.QtWidgets import QWidget, QTabBar, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QLineEdit
from PySide6.QtCore import Signal

class TabBar(QWidget):
    tab_switched = Signal(int)
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.tab_bar = QTabBar()
        self.tab_bar.setMovable(False)
        self.tab_bar.setTabsClosable(False)

        self.tab_bar.addTab("Chat")
        self.tab_bar.addTab("Settings")

        layout = QHBoxLayout()
        layout.addWidget(self.tab_bar)
        self.setLayout(layout)

        self.tab_bar.currentChanged.connect(self.tab_switched.emit)
    
    def set_current_index(self, index: int) -> None:
        self.tab_bar.setCurrentIndex(index)
    
    def get_current_index(self) -> int:
        return self.tab_bar.currentIndex()