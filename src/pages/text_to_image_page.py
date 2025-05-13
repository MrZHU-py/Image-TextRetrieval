'''
FilePath: \\Image-TextRetrieval\\src\\pages\\text_to_image_page.py
Author: ZPY
TODO: 文搜图界面
'''
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QScrollArea
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from src.image_retrieval import search_image_with_text
import os  # 导入操作系统模块
import config  # 导入配置模块

class TextToImagePage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 主布局
        main_layout = QHBoxLayout()  # 水平布局

        # 左侧布局：输入文本和检索按钮
        left_layout = QVBoxLayout()
        self.text_input = QTextEdit(self)
        self.text_input.setPlaceholderText("请输入要检索的文本...")
        left_layout.addWidget(QLabel("输入文本："))
        left_layout.addWidget(self.text_input)

        self.search_btn = QPushButton("检索相关图像", self)
        self.search_btn.clicked.connect(self.search_images)
        left_layout.addWidget(self.search_btn)

        # 右侧布局：检索结果区域
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout()
        self.results_container.setLayout(self.results_layout)
        self.scroll_area.setWidget(self.results_container)

        # 添加到主布局
        main_layout.addLayout(left_layout, stretch=1)  # 左侧占用较小空间
        main_layout.addWidget(self.scroll_area, stretch=3)  # 右侧占用较大空间

        self.setLayout(main_layout)

    def search_images(self):
        """根据输入文本检索相关图像"""
        query_text = self.text_input.toPlainText().strip()
        if not query_text:
            self.results_layout.addWidget(QLabel("请输入有效的文本！"))
            return

        try:
            # 调用检索逻辑
            results = search_image_with_text(query_text, top_k=10)

            # 清空之前的检索结果
            for i in reversed(range(self.results_layout.count())):
                self.results_layout.itemAt(i).widget().deleteLater()

            # 显示检索结果
            if results:
                for result in results:
                    # 使用索引中存储的 image_path 字段
                    image_path = result['_source'].get('image_path', '')
                    if not os.path.isabs(image_path):
                        image_path = os.path.join(config.DATA_DIR, image_path)
                    if os.path.exists(image_path):  # 确保图片路径存在
                        result_label = QLabel(self)
                        pixmap = QPixmap(image_path)
                        pixmap = pixmap.scaled(self.scroll_area.width() - 40, self.scroll_area.width() - 40, Qt.AspectRatioMode.KeepAspectRatio)
                        result_label.setPixmap(pixmap)
                        self.results_layout.addWidget(result_label)
                    else:
                        self.results_layout.addWidget(QLabel(f"图片路径无效: {image_path}"))
            else:
                self.results_layout.addWidget(QLabel("未找到相关图像。"))
        except Exception as e:
            print(f"Error in search_images: {e}")