'''
FilePath: \Image-TextRetrieval\src\pages\image_search_page.py
Author: ZPY
TODO: 图搜图界面
'''
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QScrollArea
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import os
from src.image_operations import search_image_with_clip
import config

class ImageSearchPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 主布局：水平布局
        main_layout = QHBoxLayout()

        # 左侧布局：上传图片和显示区域
        left_layout = QVBoxLayout()
        self.image_label = QLabel("未上传图片")
        self.image_label.setFixedSize(400, 600)  # 调整图片显示区域大小
        self.image_label.setStyleSheet("border: 1px solid black;")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.upload_image_btn = QPushButton("上传图片", self)
        # self.upload_image_btn.setFixedWidth(self.image_label.width())  # 按钮宽度与图片显示框一致
        self.upload_image_btn.clicked.connect(self.search_similar_images)

        # 添加到左侧布局
        left_layout.addWidget(self.image_label)
        left_layout.addWidget(self.upload_image_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # 右侧布局：检索结果显示区域
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout()
        self.results_container.setLayout(self.results_layout)
        self.scroll_area.setWidget(self.results_container)

        # 添加到主布局
        main_layout.addLayout(left_layout, stretch=1)  # 左侧占用较小空间
        main_layout.addWidget(self.scroll_area, stretch=2)  # 右侧占用较大空间

        # 设置主布局
        self.setLayout(main_layout)

    def search_similar_images(self):
        """上传图片并进行图像相似性检索"""
        try:
            # 打开文件选择对话框
            file_path, _ = QFileDialog.getOpenFileName(self, "选择图片文件", "", "图片文件 (*.png *.jpg *.jpeg)")
            if not file_path:
                return

            # 显示上传的图片
            pixmap = QPixmap(file_path)
            pixmap = pixmap.scaled(self.image_label.width(), self.image_label.height(), Qt.AspectRatioMode.KeepAspectRatio)
            self.image_label.setPixmap(pixmap)

            # 调用图像检索逻辑
            results = search_image_with_clip(file_path, top_k=10)

            # 清空之前的检索结果
            for i in reversed(range(self.results_layout.count())):
                self.results_layout.itemAt(i).widget().deleteLater()

            # 显示检索结果
            if results:
                for result in results:
                    # 使用 `_id` 字段作为图片路径
                    image_path = os.path.join(config.DATA_DIR, result['_id'])
                    if os.path.exists(image_path):  # 确保图片路径存在
                        result_label = QLabel(self)
                        pixmap = QPixmap(image_path)
                        pixmap = pixmap.scaled(self.scroll_area.width() - 40, self.scroll_area.width() - 40, Qt.AspectRatioMode.KeepAspectRatio)
                        result_label.setPixmap(pixmap)
                        self.results_layout.addWidget(result_label)
                    else:
                        self.results_layout.addWidget(QLabel(f"图片路径无效: {image_path}"))
            else:
                self.results_layout.addWidget(QLabel("未找到相似的图片。"))
        except Exception as e:
            print(f"Error in search_similar_images: {e}")