'''
FilePath: \TextRetrieval\src\gui.py
Author: ZPY
TODO: 通过 OCR 解析图片文本，并在 Elasticsearch 中进行检索
'''
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QFileDialog, QTextEdit, QVBoxLayout, QWidget
import cv2
import sys
from src.ocr_engine import extract_text_tesseract
from src.search_engine import index_text, search_text
import uuid

class ImageTextRetrievalApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Image Text Retrieval")
        self.setGeometry(100, 100, 800, 600)

        # 上传图片按钮
        self.upload_btn = QPushButton("Upload Image", self)
        self.upload_btn.clicked.connect(self.upload_image)

        # 文本显示框（显示 OCR 提取的文本）
        self.text_display = QTextEdit(self)
        self.text_display.setReadOnly(True)

        # 检索结果显示框
        self.search_results = QTextEdit(self)
        self.search_results.setReadOnly(True)

        # 布局
        layout = QVBoxLayout()
        layout.addWidget(self.upload_btn)
        layout.addWidget(QLabel("Extracted Text:"))
        layout.addWidget(self.text_display)
        layout.addWidget(QLabel("Search Results:"))
        layout.addWidget(self.search_results)
        self.setLayout(layout)

    def upload_image(self):
        """ 处理图片，进行 OCR 识别并索引到 Elasticsearch """
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            extracted_text = extract_text_tesseract(image)
            self.text_display.setText(extracted_text)

            # 生成唯一 ID 进行索引
            doc_id = str(uuid.uuid4())
            index_text(extracted_text, doc_id)

            # 进行搜索
            search_results = search_text(extracted_text)
            formatted_results = self.format_search_results(search_results)
            self.search_results.setText(formatted_results)

    def format_search_results(self, search_results):
        """ 格式化检索结果，加入序号和分隔符 """
        if not search_results:
            return "No matching results found."
        
        formatted_text = ""
        for idx, hit in enumerate(search_results, 1):
            formatted_text += f"Result {idx}:\n"
            formatted_text += f"{hit['_source']['content']}\n"
            formatted_text += "-" * 40 + "\n"
        
        return formatted_text

def main():
    app = QApplication(sys.argv)
    ex = ImageTextRetrievalApp()
    ex.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
