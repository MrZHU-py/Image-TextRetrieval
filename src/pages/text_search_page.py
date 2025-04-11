'''
FilePath: \Image-TextRetrieval\src\pages\text_search_page.py
Author: ZPY
TODO: 文搜文界面
'''
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QFileDialog
from src.image_operations import handle_text_retrieval
from src.result_formatter import format_search_results

class TextSearchPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # 上传图片按钮
        self.upload_btn = QPushButton("Upload Image for OCR", self)
        self.upload_btn.clicked.connect(self.upload_image)

        # 文本显示框（显示 OCR 提取的文本）
        self.text_display = QTextEdit(self)
        self.text_display.setReadOnly(True)

        # 检索结果显示框
        self.search_results = QTextEdit(self)
        self.search_results.setReadOnly(True)

        # 布局
        layout.addWidget(self.upload_btn)
        layout.addWidget(QLabel("Extracted Text:"))
        layout.addWidget(self.text_display)
        layout.addWidget(QLabel("Search Results:"))
        layout.addWidget(self.search_results)

        self.setLayout(layout)

    def upload_image(self):
        """上传图片并进行 OCR 和文本检索"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.jpg *.jpeg)")
            if file_path:
                extracted_text, search_results = handle_text_retrieval(file_path)
                formatted_results = format_search_results(search_results)
                self.text_display.setText(extracted_text)
                self.search_results.setText(formatted_results)
        except Exception as e:
            print(f"Error in upload_image: {e}")