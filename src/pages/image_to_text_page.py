'''
FilePath: \Image-TextRetrieval\src\pages\image_to_text_page.py
Author: ZPY
TODO: 图搜文界面
'''
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QScrollArea, QApplication
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from src.image_retrieval import search_text_with_image

class ImageToTextPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.original_texts = []  # 保存原始文本

    def initUI(self):
        """初始化界面布局"""
        # 主布局：水平布局
        main_layout = QHBoxLayout()

        # 左侧布局：上传图片和显示区域
        left_layout = QVBoxLayout()
        self.image_label = QLabel("未上传图片")
        self.image_label.setFixedSize(500, 600)  # 调整图片显示区域大小
        self.image_label.setStyleSheet("border: 1px solid black;")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.upload_btn = QPushButton("上传图片", self)
        self.upload_btn.clicked.connect(self.upload_image)

        # 添加到左侧布局
        left_layout.addWidget(self.image_label)
        left_layout.addWidget(self.upload_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # 右侧布局：检索结果显示区域
        right_layout = QVBoxLayout()
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout()
        self.results_container.setLayout(self.results_layout)
        self.scroll_area.setWidget(self.results_container)

        # 移除翻译按钮

        # 添加到右侧布局
        right_layout.addWidget(self.scroll_area, stretch=1)

        # 添加到主布局
        main_layout.addLayout(left_layout, stretch=1)
        main_layout.addLayout(right_layout, stretch=1)

        # 设置主布局
        self.setLayout(main_layout)

    def upload_image(self):
        """上传图片并检索相关文本"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "选择图片文件", "", "图片文件 (*.png *.jpg *.jpeg)")
            if not file_path:
                return

            # 显示上传的图片
            pixmap = QPixmap(file_path)
            pixmap = pixmap.scaled(self.image_label.width(), self.image_label.height(), Qt.AspectRatioMode.KeepAspectRatio)
            self.image_label.setPixmap(pixmap)

            # 调用检索逻辑
            results = search_text_with_image(file_path, top_k=10)

            # 清空之前的检索结果
            for i in reversed(range(self.results_layout.count())):
                self.results_layout.itemAt(i).widget().deleteLater()

            # 显示检索结果
            self.original_texts = []  # 清空原始文本
            if results:
                for result in results:
                    content = result['_source'].get('text', '无相关文本')  # 确保解析结果正确
                    score = result.get('_score', 0)
                    result_label = QLabel(f"相关文本: {content}\n相关度: {score:.2f}")
                    result_label.setWordWrap(True)  # 自动换行
                    self.results_layout.addWidget(result_label)
                    self.original_texts.append(content)  # 保存原始文本
            else:
                self.results_layout.addWidget(QLabel("未找到相关文本。"))
        except Exception as e:
            print(f"Error in upload_image: {e}")