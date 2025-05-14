'''
FilePath: \Image-TextRetrieval\src\pages\main_page.py
Author: ZPY
TODO: 主页面，添加快速检索与深度检索入口
'''
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtGui import QFont
from PyQt6.QtCore import pyqtSignal, Qt
from src.image_retrieval import check_es_connection
from src.pages.animated_button import AnimatedButton

class MainPage(QWidget):
    switch_requested = pyqtSignal(int)  # 1=快速,2=深度,3=OCR,4=图像,5=上传数据

    def __init__(self):
        super().__init__()
        check_es_connection()
        self.init_ui()

    def init_ui(self):
        # 绑定主布局
        main_layout = QVBoxLayout(self)

        # 顶部标题区
        title = QLabel("基于图像的文本检索系统")
        title.setFont(QFont("微软雅黑", 28, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle = QLabel("作者：ZPY")
        subtitle.setFont(QFont("微软雅黑", 14))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addSpacing(60)

        # 中部三大功能按钮：OCR、快速、深度
        mid_layout = QHBoxLayout()
        mid_layout.setSpacing(5)
        specs = [
            ("OCR检索", 3, "#8fb339"),
            ("快速检索", 1, "#83c9d8"),
            ("深度检索", 2, "#f29f05"),
        ]
        for label, idx, color in specs:
            btn = AnimatedButton(
                label=label,
                idx=idx,
                color=color,
                normal_size=(220, 100),
                hover_scale=1.15,
                font_size=22,
                parent=self
            )
            btn.clicked.connect(lambda _, i=idx: self.switch_requested.emit(i))
            mid_layout.addWidget(btn)

        # 新增：用QWidget包裹中部按钮并设置固定高度
        mid_widget = QWidget()
        mid_widget.setLayout(mid_layout)
        mid_widget.setFixedHeight(140)  # 可根据按钮动画最大高度调整

        main_layout.addWidget(mid_widget)
        main_layout.addSpacing(60)

        # 下部两小按钮：图像检索、上传数据
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)
        bottom_layout.addStretch(1)
        bottom_specs = [
            ("图像检索", 4, "#a3a3a3"),
            ("上传数据", 5, "#7ed3d1"),
        ]
        for label, idx, color in bottom_specs:
            btn = AnimatedButton(
                label=label,
                idx=idx,
                color=color,
                normal_size=(140, 70),
                hover_scale=1.15,
                font_size=14,
                parent=self
            )
            btn.clicked.connect(lambda _, i=idx: self.switch_requested.emit(i))
            bottom_layout.addWidget(btn)
        bottom_layout.addStretch(1)
        main_layout.addLayout(bottom_layout)
        main_layout.addStretch(2)