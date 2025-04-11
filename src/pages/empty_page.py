'''
FilePath: \\Image-TextRetrieval\\src\\pages\\empty_page.py
Author: ZPY
TODO: 
'''
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class EmptyPage(QWidget):
    def __init__(self, message):
        super().__init__()
        self.initUI(message)

    def initUI(self, message):
        layout = QVBoxLayout()
        layout.addWidget(QLabel(message))
        self.setLayout(layout)