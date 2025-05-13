'''
FilePath: \Image-TextRetrieval\src\pages\main_page.py
Author: ZPY
TODO: 
'''
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtGui import QFont
from PyQt6.QtCore import pyqtSignal, Qt

class MainPage(QWidget):
    switch_requested = pyqtSignal(int)  # 0=主页面，1=文搜文，2=图搜图，3=文搜图，4=图搜文，5=上传数据

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        # 上部：系统名称和作者
        title = QLabel("基于图像的文本检索系统\n")
        title.setFont(QFont("微软雅黑", 22, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        author = QLabel("作者：ZPY")
        author.setFont(QFont("微软雅黑", 12))
        author.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        main_layout.addWidget(author)
        main_layout.addStretch(1)

        # 中部：四个功能按钮
        btn_layout = QHBoxLayout()
        btn_names = ["文搜文", "图搜图", "文搜图", "图搜文"]
        for i, name in enumerate(btn_names):
            btn = QPushButton(name)
            btn.setFixedSize(140, 60)
            btn.setFont(QFont("微软雅黑", 13, QFont.Weight.Bold))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #83c9d8; color: white; border-radius: 15px;
                }
                QPushButton:hover {
                    background-color: #4ca0c8;
                }
            """)
            btn.clicked.connect(lambda _, idx=i+1: self.switch_requested.emit(idx))
            btn_layout.addWidget(btn)
        main_layout.addLayout(btn_layout)

        # 下部：存入数据按钮
        btn_data = QPushButton("上传数据")
        btn_data.setFixedSize(90, 40)
        btn_data.setFont(QFont("微软雅黑", 12))
        btn_data.setStyleSheet("""
            QPushButton {
                background-color: #7ed3d1; color: white; border-radius: 13px;
            }
            QPushButton:hover {
                background-color: #3bb5b5;
            }
        """)
        btn_data.clicked.connect(lambda: self.switch_requested.emit(5))  # 5代表上传数据页面
        main_layout.addStretch(2)
        main_layout.addWidget(btn_data, alignment=Qt.AlignmentFlag.AlignRight)
        self.setLayout(main_layout)
