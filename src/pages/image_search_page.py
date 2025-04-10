from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QFileDialog, QScrollArea
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
        layout = QVBoxLayout()

        # 上传图片按钮和显示区域
        self.image_label = QLabel(self)
        self.image_label.setText("No Image Uploaded")
        self.image_label.setFixedSize(300, 300)
        self.image_label.setStyleSheet("border: 1px solid black;")
        self.upload_image_btn = QPushButton("Upload Image", self)
        self.upload_image_btn.clicked.connect(self.search_similar_images)

        # 滑动区域显示检索结果
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout()
        self.results_container.setLayout(self.results_layout)
        self.scroll_area.setWidget(self.results_container)

        # 布局
        layout.addWidget(self.image_label)
        layout.addWidget(self.upload_image_btn)
        layout.addWidget(QLabel("Search Results:"))
        layout.addWidget(self.scroll_area)
        self.setLayout(layout)

    def search_similar_images(self):
        """上传图片并进行图像相似性检索"""
        try:
            # 打开文件选择对话框
            file_path, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.jpg *.jpeg)")
            if not file_path:
                print("No file selected.")
                return

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
                    result_pixmap = result_pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio)
                    result_label.setPixmap(result_pixmap)
                    self.results_layout.addWidget(result_label)
        except Exception as e:
            print(f"Error in search_similar_images: {e}")