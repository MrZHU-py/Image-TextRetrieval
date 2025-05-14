'''
FilePath: \Image-TextRetrieval\src\pages\advanced_image_search_page.py
Author: ZPY
TODO: 图像检索界面（支持上传图像、文本或图+文联合检索），修复函数调用签名
'''
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QTextEdit, QLabel,
    QFileDialog, QScrollArea, QSizePolicy
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal
import os
from src.image_retrieval import search_image_with_text, search_image_with_clip
import config

class AdvancedImageSearchPage(QWidget):
    switch_back = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.image_path = None
        self.init_ui()

    def init_ui(self):
        # 主布局：左右分区
        main_layout = QHBoxLayout(self)

        # 左侧操作区
        left_layout = QVBoxLayout()
        left_layout.setSpacing(10)

        # 返回按钮
        back_btn = QPushButton("← 返回")
        back_btn.setFixedSize(100, 30)
        back_btn.clicked.connect(self.switch_back.emit)
        left_layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        # 图片预览
        self.preview = QLabel("未上传图片")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setStyleSheet("border:1px solid #ccc;")
        self.preview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        left_layout.addWidget(self.preview, stretch=1)

        # 上传与清除按钮
        btns_layout = QHBoxLayout()
        self.upload_btn = QPushButton("上传图片")
        self.upload_btn.setFixedWidth(100)
        self.upload_btn.clicked.connect(self.upload_image)
        btns_layout.addWidget(self.upload_btn)
        self.clear_btn = QPushButton("清除图片")
        self.clear_btn.setFixedWidth(100)
        self.clear_btn.clicked.connect(self.clear_image)
        btns_layout.addWidget(self.clear_btn)
        left_layout.addLayout(btns_layout)

        # 文本输入
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("可选：输入辅助描述文本...")
        self.text_input.setFixedHeight(60)
        left_layout.addWidget(self.text_input)

        # 搜索按钮
        self.search_btn = QPushButton("开始检索")
        self.search_btn.clicked.connect(self.search)
        left_layout.addWidget(self.search_btn)

        main_layout.addLayout(left_layout, stretch=2)

        # 右侧结果区
        right_layout = QVBoxLayout()
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        container = QWidget()
        self.results_layout = QVBoxLayout(container)
        self.scroll.setWidget(container)
        right_layout.addWidget(self.scroll)

        main_layout.addLayout(right_layout, stretch=3)
        self.setLayout(main_layout)

    def upload_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", "图片 (*.png *.jpg *.jpeg *.bmp)"
        )
        if path:
            self.image_path = path
            # 缩放并显示
            pix = QPixmap(path).scaled(
                self.preview.width(), self.preview.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.preview.setPixmap(pix)

    def clear_image(self):
        """清除已上传图片，避免对文本检索图像造成干扰"""
        self.image_path = None
        self.preview.clear()
        self.preview.setText("未上传图片")

    def search(self):
        text = self.text_input.toPlainText().strip()
        results = []
        # 图像优先检索
        if self.image_path:
            img_hits = search_image_with_clip(self.image_path, top_k=10)
            if text:
                # 文本辅助筛选：仅保留文本与图像检索结果中的匹配项
                refined = []
                for hit in img_hits:
                    # 使用文本检索确认一致性
                    candidates = search_image_with_text(text, top_k=1)
                    if candidates and candidates[0].get('_id') == hit.get('_id'):
                        refined.append(hit)
                results = refined if refined else img_hits
            else:
                results = img_hits
        # 仅文本检索
        elif text:
            results = search_image_with_text(text, top_k=10)

        # 清空旧结果
        for i in reversed(range(self.results_layout.count())):
            widget = self.results_layout.takeAt(i).widget()
            if widget:
                widget.deleteLater()

        # 渲染结果
        if not results:
            self.results_layout.addWidget(QLabel("未找到相关图像。"))
            return
        for hit in results:
            rel = hit['_source'].get('image_path', '') or hit.get('_id', '')
            img_path = rel if os.path.isabs(rel) else os.path.join(config.DATA_DIR, rel)
            lbl = QLabel()
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if os.path.exists(img_path):
                pix = QPixmap(img_path).scaled(
                    400, 400,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                lbl.setPixmap(pix)
            else:
                lbl.setText(f"无效路径: {img_path}")
            self.results_layout.addWidget(lbl)