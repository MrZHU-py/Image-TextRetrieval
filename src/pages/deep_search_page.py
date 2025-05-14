'''
FilePath: \Image-TextRetrieval\src\pages\deep_search_page.py
Author: ZPY
TODO: 深度检索界面（含返回功能和深度检索逻辑挂载）
'''
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QTextBrowser
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap
from src.image_retrieval import search_deep_text_with_image
from src.result_formatter import format_search_results

class DeepSearchPage(QWidget):
    switch_back = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()
        self.original_texts = []  # 保存原始文本

    def initUI(self):
        """初始化界面布局"""
        main_layout = QHBoxLayout()

        # 左侧: 返回按钮 + 上传图片区域
        left_layout = QVBoxLayout()
        back_btn = QPushButton("← 返回")
        back_btn.setFixedSize(100, 30)
        back_btn.clicked.connect(self.switch_back.emit)
        left_layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        self.image_label = QLabel("未上传图片")
        self.image_label.setFixedSize(500, 600)
        self.image_label.setStyleSheet("border: 1px solid black;")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.image_label)

        self.upload_btn = QPushButton("上传图片")
        self.upload_btn.setFixedSize(100, 30)
        self.upload_btn.clicked.connect(self.upload_image)
        left_layout.addWidget(self.upload_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # 右侧: 深度检索结果显示 QTextBrowser
        right_layout = QVBoxLayout()
        self.results_browser = QTextBrowser()
        self.results_browser.setReadOnly(True)
        self.results_browser.setOpenExternalLinks(True)
        right_layout.addWidget(self.results_browser)

        main_layout.addLayout(left_layout, stretch=1)
        main_layout.addLayout(right_layout, stretch=1)
        self.setLayout(main_layout)

    def upload_image(self):
        """上传图片并检索相关文本"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(self,
                                                       "选择图片文件",
                                                       "",
                                                       "图片文件 (*.png *.jpg *.jpeg)")
            if not file_path:
                return

            # 显示上传的图片
            pixmap = QPixmap(file_path).scaled(
                self.image_label.width(),
                self.image_label.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(pixmap)

            # 调用深度检索逻辑
            results = search_deep_text_with_image(image_path=file_path, top_k_clip=10)
            html = format_search_results(results)

            # 显示在 QTextBrowser
            self.results_browser.setHtml(html)

        except Exception as e:
            print(f"Error in upload_image: {e}")