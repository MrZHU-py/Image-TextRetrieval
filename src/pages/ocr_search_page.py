'''
FilePath: \\Image-TextRetrieval\\src\\pages\\ocr_search_page.py
# Author: ZPY
# TODO: 即时OCR检索+编辑重试界面（自适应布局，图片区域动态伸缩）
'''
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QTextBrowser, QDialog, QTextEdit, QSpacerItem, QSizePolicy
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal
import gc
from src.preprocessing import preprocess_image
from src.ocr_engine import extract_text_ocr
from src.text_retrieval import search_text
from src.result_formatter import format_search_results

class OCRSearchPage(QWidget):
    switch_back = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ocr_text = ""
        self.pixmap = None
        self.init_ui()

    def init_ui(self):
        # 主布局：左右分区
        main_layout = QHBoxLayout(self)

        # 左侧：图像框 + 上传按钮
        left_layout = QVBoxLayout()

        # 返回按钮
        back_btn = QPushButton("← 返回")
        back_btn.setFixedSize(100, 30)
        back_btn.clicked.connect(self.switch_back.emit)
        left_layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        # 图片展示，自适应伸缩，但不让 QLabel 因 pixmap 改变自己的 sizeHint
        self.image_label = QLabel("未上传图片")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid black;")
        self.image_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        left_layout.addWidget(self.image_label, stretch=1)

        # 上传按钮
        btn_layout = QHBoxLayout()
        btn_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.upload_btn = QPushButton("上传并OCR检索")
        self.upload_btn.clicked.connect(self.upload_and_search)
        btn_layout.addWidget(self.upload_btn)
        btn_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        left_layout.addLayout(btn_layout)

        # 填充
        left_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        main_layout.addLayout(left_layout, stretch=1)

        # 右侧：结果区 + 编辑提示
        right_layout = QVBoxLayout()
        self.result_view = QTextBrowser()
        self.result_view.setOpenExternalLinks(True)
        right_layout.addWidget(self.result_view, stretch=1)

        # 编辑提示区域
        prompt_layout = QHBoxLayout()
        self.prompt_label = QLabel("对检索结果不满意？编辑文本重试→")
        self.prompt_label.setStyleSheet("color: gray;")
        self.edit_btn = QPushButton("编辑")
        self.edit_btn.clicked.connect(self.open_edit_dialog)
        prompt_layout.addWidget(self.prompt_label)
        prompt_layout.addWidget(self.edit_btn)
        prompt_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        right_layout.addLayout(prompt_layout)

        main_layout.addLayout(right_layout, stretch=1)
        self.setLayout(main_layout)

        # 初始隐藏编辑区
        self.prompt_label.hide()
        self.edit_btn.hide()

    def resizeEvent(self, event):
        # 只在 self.pixmap 不为空时，才按当前 QLabel 大小做等比例缩放
        if self.pixmap:
            scaled = self.pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)
        super().resizeEvent(event)

    def upload_and_search(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", "图片 (*.png *.jpg *.jpeg *.bmp)"
        )
        if not path:
            return

        # 1. 读取并存储原始 pixmap
        self.pixmap = QPixmap(path)
        if self.pixmap.isNull():
            return

        # 2. “初次缩放”——直接用 image_label 当前大小做一次等比例缩放并 setPixmap
        scaled = self.pixmap.scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(scaled)

        # 3. OCR 提取逻辑（保持你现有的流程）
        _, proc = preprocess_image(path)
        text = extract_text_ocr(proc) or ""
        self.ocr_text = text
        del proc; gc.collect()

        # 4. 文本检索并显示
        hits = search_text(text, top_k=10)
        html = format_search_results(hits)
        self.result_view.setHtml(html)

        # 5. 显示“编辑”提示
        self.prompt_label.show()
        self.edit_btn.show()

    def open_edit_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("编辑并重试")
        vbox = QVBoxLayout(dlg)
        text_edit = QTextEdit()
        text_edit.setPlainText(self.ocr_text)
        vbox.addWidget(text_edit)
        hbox = QHBoxLayout()
        retry_btn = QPushButton("检索")
        retry_btn.clicked.connect(lambda: self._retry_search(text_edit.toPlainText(), dlg))
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dlg.reject)
        hbox.addWidget(retry_btn)
        hbox.addWidget(cancel_btn)
        vbox.addLayout(hbox)
        dlg.exec()

    def _retry_search(self, new_text, dialog):
        self.ocr_text = new_text
        hits = search_text(new_text, top_k=10)
        html = format_search_results(hits)
        self.result_view.setHtml(html)
        dialog.accept()
