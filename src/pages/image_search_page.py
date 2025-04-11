'''
FilePath: \Image-TextRetrieval\src\pages\image_search_page.py
Author: ZPY
TODO: 图搜图界面
'''
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QScrollArea
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import os
import config
from src.image_operations import handle_image_retrieval

class ImageSearchPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 主布局：水平布局，左侧为上传区域，右侧为检索结果
        main_layout = QHBoxLayout()

        # 左侧布局：上传图片和显示区域
        left_layout = QVBoxLayout()

        # 上传图片按钮和显示区域
        self.image_label = QLabel(self)
        self.image_label.setText("No Image Uploaded")
        self.image_label.setFixedSize(400, 400)  # 调整上传图片显示区域大小
        self.image_label.setStyleSheet("border: 1px solid black;")
        self.upload_image_btn = QPushButton("Upload Image", self)
        self.upload_image_btn.clicked.connect(self.search_similar_images)

        # 添加到左侧布局
        left_layout.addWidget(self.image_label)
        left_layout.addWidget(self.upload_image_btn)

        # 右侧布局：检索结果
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout()
        self.results_container.setLayout(self.results_layout)
        self.scroll_area.setWidget(self.results_container)

        # 设置滚动区域的宽度
        self.scroll_area.setFixedWidth(300)

        # 添加到主布局
        main_layout.addLayout(left_layout)
        main_layout.addWidget(self.scroll_area)

        # 设置主布局
        self.setLayout(main_layout)

    def search_similar_images(self):
        """上传图片并进行图像相似性检索"""
        try:
            # 打开文件选择对话框
            file_path, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.jpg *.jpeg)")
            if not file_path:
                print("No file selected.")
                return

            # 确保路径兼容性（解决中文路径问题）
            file_path = os.path.normpath(file_path)

            # 显示上传的图片
            pixmap = QPixmap(file_path)
            pixmap = pixmap.scaled(self.image_label.width(), self.image_label.height(), Qt.AspectRatioMode.KeepAspectRatio)
            self.image_label.setPixmap(pixmap)

            # 调用图像检索逻辑
            hash_ids = handle_image_retrieval(file_path)
            if not hash_ids:
                self.results_layout.addWidget(QLabel("No similar images found."))
                return

            # 清空之前的检索结果
            for i in reversed(range(self.results_layout.count())):
                self.results_layout.itemAt(i).widget().deleteLater()

            # 显示检索结果
            for hash_id in hash_ids:
                image_path = os.path.join(config.DATA_DIR, f"{hash_id}.jpg")
                if os.path.exists(image_path):
                    result_label = QLabel(self)
                    result_pixmap = QPixmap(image_path)
                    result_pixmap = result_pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)  # 调整检索结果图片大小
                    result_label.setPixmap(result_pixmap)
                    self.results_layout.addWidget(result_label)
        except Exception as e:
            print(f"Error in search_similar_images: {e}")