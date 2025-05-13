'''
FilePath: \Image-TextRetrieval\src\pages\text_search_page.py
Author: ZPY
TODO: 文搜文界面
'''
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QFileDialog, QTextBrowser
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from src.preprocessing import preprocess_image
from src.ocr_engine import extract_text_ocr
from src.image_operations import handle_text_retrieval
from src.result_formatter import format_search_results
from src.text_retrieval import search_text
import gc  # 新增：用于手动垃圾回收

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
        self.original_image_label.setFixedSize(500, 300)
        self.original_image_label.setStyleSheet("border: 1px solid black;")
        self.original_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 图片居中显示

        self.processed_image_label = QLabel("处理后图像")
        self.processed_image_label.setFixedSize(500, 300)
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
        self.search_results = QTextBrowser(self)
        self.search_results.setPlaceholderText("检索结果将在此显示...")
        self.search_results.setReadOnly(True)
        self.search_results.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.search_results.setOpenExternalLinks(True)  # 允许打开外部链接

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
        """上传图片并进行整图 OCR 和文本检索"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, 
                "选择图片文件", 
                "", 
                "图片文件 (*.png *.jpg *.jpeg *.bmp)"
            )
            if not file_path:
                return

            self.text_display.clear()
            self.search_results.clear()

            # 显示原图
            pixmap = QPixmap(file_path)
            pixmap = pixmap.scaled(
                self.original_image_label.width(),
                self.original_image_label.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.original_image_label.setPixmap(pixmap)

            # 预处理图片，直接整图OCR
            orig_img, processed_img = preprocess_image(file_path)

            # 显示处理后图像
            height, width, _ = processed_img.shape
            bytes_per_line = 3 * width
            q_image = QImage(processed_img.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            processed_pixmap = QPixmap.fromImage(q_image)
            processed_pixmap = processed_pixmap.scaled(
                self.processed_image_label.width(),
                self.processed_image_label.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.processed_image_label.setPixmap(processed_pixmap)

            # 整图OCR
            extracted_text = extract_text_ocr(processed_img)

            # 检索
            if extracted_text:
                search_results = search_text(extracted_text, top_k=10)
            else:
                search_results = []

            # 显示提取的文本
            if extracted_text:
                self.text_display.setText(extracted_text)
            else:
                self.text_display.setText("未提取到文本内容。")

            # 显示检索结果
            if search_results:
                formatted_results = format_search_results(search_results)
                self.search_results.setHtml(formatted_results)  # 显示为 HTML 格式以实现超链接跳转
            else:
                self.search_results.setHtml("未找到相关内容。")

            # 主动释放内存
            del orig_img, processed_img
            gc.collect()
        except Exception as e:
            self.text_display.setText(f"图片处理失败: {e}")
            self.search_results.setText("")

    def search_text(self):
        """根据提取的文本进行检索"""
        try:
            query_text = self.text_display.toPlainText()
            if not query_text.strip():
                self.search_results.setText("请输入要检索的文本！")
                return

            # 调用文本检索逻辑
            search_results = search_text(query_text, top_k=10)

            # 显示检索结果
            if search_results:
                formatted_results = format_search_results(search_results)
                self.search_results.setHtml(formatted_results)
            else:
                self.search_results.setHtml("未找到相关内容。")
        except Exception as e:
            self.search_results.setText(f"检索失败: {e}")