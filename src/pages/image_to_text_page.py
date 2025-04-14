'''
FilePath: \Image-TextRetrieval\src\pages\image_to_text_page.py
Author: ZPY
TODO: 图搜文界面
'''
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QScrollArea, QApplication
from PyQt6.QtGui import QPixmap, QMovie
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from src.image_operations import search_text_with_image
from googletrans import Translator  # 导入翻译模块

class TranslationThread(QThread):
    """后台翻译线程"""
    translation_done = pyqtSignal(list)  # 信号：翻译完成，传递翻译后的文本列表

    def __init__(self, texts, parent=None):
        super().__init__(parent)
        self.texts = texts
        self.translator = Translator()

    def run(self):
        """执行翻译任务"""
        translated_texts = []
        for text in self.texts:
            try:
                translated_text = self.translator.translate(text, src="en", dest="zh-cn").text
                translated_texts.append(translated_text)
            except Exception as e:
                translated_texts.append(f"翻译失败: {e}")
        self.translation_done.emit(translated_texts)  # 发射信号，传递翻译结果


class ImageToTextPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.translator = Translator()  # 初始化翻译器
        self.is_translated = False  # 标记当前是否为翻译状态
        self.original_texts = []  # 保存原始文本
        self.translation_thread = None  # 后台翻译线程

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

        # 添加翻译按钮
        self.translate_btn = QPushButton("翻译", self)
        self.translate_btn.clicked.connect(self.toggle_translation)

        # 添加到右侧布局
        right_layout.addWidget(self.scroll_area, stretch=1)
        right_layout.addWidget(self.translate_btn, alignment=Qt.AlignmentFlag.AlignCenter)

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
                    content = result['_source'].get('content', '无相关文本')  # 确保解析结果正确
                    score = result.get('_score', 0)
                    result_label = QLabel(f"相关文本: {content}\n相关度: {score:.2f}")
                    result_label.setWordWrap(True)  # 自动换行
                    self.results_layout.addWidget(result_label)
                    self.original_texts.append(content)  # 保存原始文本
            else:
                self.results_layout.addWidget(QLabel("未找到相关文本。"))
        except Exception as e:
            print(f"Error in upload_image: {e}")

    def toggle_translation(self):
        """切换翻译和显示原文"""
        try:
            if not self.original_texts:
                return

            # 清空之前的检索结果
            # for i in reversed(range(self.results_layout.count())):
            #     self.results_layout.itemAt(i).widget().deleteLater()

            if not self.is_translated:
                # 启动后台翻译线程
                self.translation_thread = TranslationThread(self.original_texts)
                self.translation_thread.translation_done.connect(self.display_translated_texts)
                self.translation_thread.start()
            else:
                # 显示原文
                self.display_original_texts()
        except Exception as e:
            print(f"Error in toggle_translation: {e}")

    def display_translated_texts(self, translated_texts):
        """显示翻译后的文本"""
        # 清空之前的检索结果
        for i in reversed(range(self.results_layout.count())):
            self.results_layout.itemAt(i).widget().deleteLater()

        for text in translated_texts:
            result_label = QLabel(f"翻译文本: {text}")
            result_label.setWordWrap(True)
            self.results_layout.addWidget(result_label)

        self.translate_btn.setText("显示原文")
        self.is_translated = True

        # 启用翻译按钮
        self.translate_btn.setEnabled(True)

    def display_original_texts(self):
        """显示原文"""
        # 清空之前的检索结果
        for i in reversed(range(self.results_layout.count())):
            self.results_layout.itemAt(i).widget().deleteLater()

        for text in self.original_texts:
            result_label = QLabel(f"相关文本: {text}")
            result_label.setWordWrap(True)
            self.results_layout.addWidget(result_label)

        self.translate_btn.setText("翻译")
        self.is_translated = False

        # 启用翻译按钮
        self.translate_btn.setEnabled(True)