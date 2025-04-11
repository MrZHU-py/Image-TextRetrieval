'''
FilePath: \Image-TextRetrieval\src\pages\text_search_page.py
Author: ZPY
TODO: 文搜文界面
'''
import cv2
import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QFileDialog
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from src.preprocessing import preprocess_image  # 调用预处理模块
from src.image_operations import handle_text_retrieval
from src.result_formatter import format_search_results
from src.text_retrieval import search_text

class TextSearchPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 主布局
        main_layout = QVBoxLayout()

        # 顶部图片显示区域
        image_layout = QHBoxLayout()
        self.original_image_label = QLabel("原图")
        self.original_image_label.setFixedSize(300, 300)
        self.original_image_label.setStyleSheet("border: 1px solid black;")
        self.original_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 图片居中显示

        self.processed_image_label = QLabel("处理后图像")
        self.processed_image_label.setFixedSize(300, 300)
        self.processed_image_label.setStyleSheet("border: 1px solid black;")
        self.processed_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 图片居中显示

        image_layout.addWidget(self.original_image_label)
        image_layout.addWidget(self.processed_image_label)

        # 中部文本框和按钮区域
        text_layout = QVBoxLayout()
        self.upload_btn = QPushButton("上传图片", self)
        self.upload_btn.clicked.connect(self.upload_image)

        self.text_display = QTextEdit(self)
        self.text_display.setPlaceholderText("提取的文本将在此显示...")
        self.text_display.setReadOnly(False)  # 设置为可编辑

        text_layout.addWidget(self.upload_btn)
        text_layout.addWidget(QLabel("提取的文本："))
        text_layout.addWidget(self.text_display)

        # 底部检索结果和按钮区域
        results_layout = QHBoxLayout()
        self.search_results = QTextEdit(self)
        self.search_results.setPlaceholderText("检索结果将在此显示...")
        self.search_results.setReadOnly(True)

        self.search_btn = QPushButton("检索", self)
        self.search_btn.clicked.connect(self.search_text)

        results_layout.addWidget(self.search_results)
        results_layout.addWidget(self.search_btn)

        # 将所有布局添加到主布局
        main_layout.addLayout(image_layout)
        main_layout.addLayout(text_layout)
        main_layout.addLayout(results_layout)

        self.setLayout(main_layout)

    def upload_image(self):
        """上传图片并进行 OCR 和文本检索"""
        try:
            # 打开文件选择对话框
            file_path, _ = QFileDialog.getOpenFileName(self, "选择图片文件", "", "图片文件 (*.png *.jpg *.jpeg)")
            if file_path:
                # 清空文本框内容
                self.text_display.clear()
                self.search_results.clear()

                # 显示原图
                pixmap = QPixmap(file_path)
                pixmap = pixmap.scaled(
                    self.original_image_label.width(),
                    self.original_image_label.height(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation  # 使用平滑缩放
                )
                self.original_image_label.setPixmap(pixmap)

                # 调用预处理模块处理图像
                processed_image = preprocess_image(file_path)

                # 显示处理后的图像
                if processed_image is not None:
                    height, width = processed_image.shape[:2]
                    bytes_per_line = width
                    if len(processed_image.shape) == 3:  # 如果是彩色图像
                        bytes_per_line = 3 * width
                        q_image = QImage(processed_image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
                    else:  # 如果是灰度图像
                        q_image = QImage(processed_image.data, width, height, bytes_per_line, QImage.Format.Format_Grayscale8)

                    processed_pixmap = QPixmap.fromImage(q_image)
                    processed_pixmap = processed_pixmap.scaled(
                        self.processed_image_label.width(),
                        self.processed_image_label.height(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation  # 使用平滑缩放
                    )
                    self.processed_image_label.setPixmap(processed_pixmap)

                # 调用 OCR 和检索逻辑
                extracted_text, search_results = handle_text_retrieval(file_path)

                # 显示提取的文本
                if extracted_text:
                    self.text_display.setText(extracted_text)
                else:
                    self.text_display.setText("未提取到文本内容。")

                # 显示检索结果
                if search_results:
                    formatted_results = format_search_results(search_results)
                    self.search_results.setText(formatted_results)
                else:
                    self.search_results.setText("未找到相关内容。")
        except Exception as e:
            print(f"Error in upload_image: {e}")

    def search_text(self):
        """根据提取的文本进行检索"""
        try:
            query_text = self.text_display.toPlainText()
            if not query_text.strip():
                self.search_results.setText("请输入要检索的文本！")
                return

            # 调用文本检索逻辑
            search_results = search_text(query_text, top_k=5)

            # 显示检索结果
            if search_results:
                formatted_results = format_search_results(search_results)
                self.search_results.setText(formatted_results)
            else:
                self.search_results.setText("未找到相关内容。")
        except Exception as e:
            print(f"Error in search_text: {e}")