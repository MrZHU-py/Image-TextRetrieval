'''
FilePath: \\Image-TextRetrieval\\src\\pages\\deep_search_page.py
Author: ZPY
TODO: 深度检索界面（含返回功能和深度检索逻辑挂载）
'''
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QTextBrowser, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap
from src.image_retrieval import search_deep_text_with_image
from src.result_formatter import format_search_results

class DeepSearchPage(QWidget):
    switch_back = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.pixmap = None               # 用来保存原始 QPixmap
        self.original_texts = []         # 保存原始文本
        self.initUI()

    def initUI(self):
        """初始化界面布局（自适应、等比例缩放）"""
        main_layout = QHBoxLayout(self)

        # 左侧: 返回按钮 + 上传图片区域
        left_layout = QVBoxLayout()

        back_btn = QPushButton("← 返回")
        back_btn.setFixedSize(100, 30)
        back_btn.clicked.connect(self.switch_back.emit)
        left_layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        # 图片展示区：不让 QLabel 因 pixmap 改变自己的 sizeHint
        self.image_label = QLabel("未上传图片")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid black;")
        self.image_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        left_layout.addWidget(self.image_label, stretch=1)

        # 上传按钮
        self.upload_btn = QPushButton("上传图片")
        self.upload_btn.clicked.connect(self.upload_image)
        left_layout.addWidget(self.upload_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        left_layout.addSpacerItem(QSpacerItem(
            20, 20,
            QSizePolicy.Policy.Minimum,
            QSizePolicy.Policy.Expanding
        ))
        main_layout.addLayout(left_layout, stretch=1)

        # 右侧: 深度检索结果显示 QTextBrowser
        right_layout = QVBoxLayout()
        self.results_browser = QTextBrowser()
        self.results_browser.setReadOnly(True)
        self.results_browser.setOpenExternalLinks(True)
        right_layout.addWidget(self.results_browser, stretch=1)
        main_layout.addLayout(right_layout, stretch=1)

        self.setLayout(main_layout)

    def resizeEvent(self, event):
        """窗口尺寸变化时，对已加载的 pixmap 做等比例缩放并展示"""
        if self.pixmap:
            # 按当前 QLabel 的大小做 KeepAspectRatio 缩放
            scaled = self.pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            # 把缩放后的图贴到 QLabel
            self.image_label.setPixmap(scaled)
        # 调用父类的 resizeEvent
        super().resizeEvent(event)

    def upload_image(self):
        """上传图片并执行深度检索"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "选择图片文件",
                "",
                "图片文件 (*.png *.jpg *.jpeg)"
            )
            if not file_path:
                return

            # 1. 读取原始 QPixmap，并保存在 self.pixmap
            orig = QPixmap(file_path)
            if orig.isNull():
                return
            self.pixmap = orig

            # 2. 初次缩放：用当前 QLabel 的大小做一次等比例缩放并 setPixmap
            scaled = self.pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)

            # 3. 调用深度检索逻辑
            results = search_deep_text_with_image(image_path=file_path, top_k_clip=10)
            html = format_search_results(results)

            # 4. 将检索结果显示到 QTextBrowser
            self.results_browser.setHtml(html)

        except Exception as e:
            print(f"Error in upload_image: {e}")
