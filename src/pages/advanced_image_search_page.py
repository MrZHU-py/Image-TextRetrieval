'''
FilePath: \\Image-TextRetrieval\\src\\pages\\advanced_image_search_page.py
Author: ZPY
TODO: 图像检索界面（支持上传图像、文本或图+文联合检索），修复函数调用签名
'''
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QTextEdit, QLabel,
    QFileDialog, QScrollArea, QSizePolicy, QDialog, QMainWindow, QSpacerItem
)
from PyQt6.QtGui import QPixmap, QMouseEvent
from PyQt6.QtCore import Qt, pyqtSignal, QSize
import os
from src.image_retrieval import (
    search_image_with_clip,
    search_image_with_text,
    search_image_with_clip_and_text  # 新增联合检索函数
)
import config


class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置鼠标形状
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class ImagePopup(QMainWindow):
    def __init__(self, pixmap: QPixmap, parent=None):
        super().__init__(parent)
        self.setWindowTitle("图片预览")
        self.pixmap = pixmap

        # 主部件和布局
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 不让 label 因 pixmap 改变自身大小
        self.image_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        layout.addWidget(self.image_label)

        # 初次显示时按当前对话框大小缩放
        self.update_image()

    def resizeEvent(self, event):
        self.update_image()
        super().resizeEvent(event)

    def update_image(self):
        if not self.pixmap.isNull():
            # 按整窗大小做等比例缩放
            scaled_pix = self.pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pix)


class AdvancedImageSearchPage(QWidget):
    switch_back = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.pixmap = None
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

        # 图片预览：改为 Ignored，使用 resizeEvent 手动缩放以实现图片随窗口大小变化而等比例缩放                                            
        self.preview = QLabel("未上传图片")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setStyleSheet("border:1px solid #ccc;")
        self.preview.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        # 可选：设置最小尺寸防止窗口过小时看不到
        self.preview.setMinimumSize(200, 200)
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

        # 左侧底部留白
        left_layout.addSpacerItem(QSpacerItem(
            20, 20,
            QSizePolicy.Policy.Minimum,
            QSizePolicy.Policy.Expanding
        ))

        main_layout.addLayout(left_layout, stretch=2)

        # 右侧结果区
        right_layout = QVBoxLayout()
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        container = QWidget()
        self.results_layout = QVBoxLayout(container)
        self.scroll.setWidget(container)
        right_layout.addWidget(self.scroll, stretch=1)
        main_layout.addLayout(right_layout, stretch=3)

        self.setLayout(main_layout)

    def resizeEvent(self, event):
        # 当主窗口大小变化时，如果有原始 pixmap，就按 preview 大小等比例缩放
        if self.pixmap and not self.pixmap.isNull():
            scaled = self.pixmap.scaled(
                self.preview.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.preview.setPixmap(scaled)
        super().resizeEvent(event)

    def upload_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", "图片 (*.png *.jpg *.jpeg *.bmp)"
        )
        if path:
            self.image_path = path

            # 1. 读取原始 QPixmap 并保存
            orig_pix = QPixmap(path)
            if orig_pix.isNull():
                return
            self.pixmap = orig_pix

            # 2. 初次缩放展示：按当前 preview 大小做一次等比例缩放
            scaled = self.pixmap.scaled(
                self.preview.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.preview.setPixmap(scaled)

    def clear_image(self):
        """清除已上传图片，恢复默认文本"""
        self.image_path = None
        self.pixmap = None
        self.preview.clear()
        self.preview.setText("未上传图片")

    def search(self):
        text = self.text_input.toPlainText().strip()
        # 根据是否上传图像和文本来选择检索方式
        if self.image_path and text:
            # 图+文联合检索
            results = search_image_with_clip_and_text(self.image_path, text, top_k=10)
        elif self.image_path:
            # 仅图像检索
            results = search_image_with_clip(self.image_path, top_k=10)
        elif text:
            # 仅文本检索
            results = search_image_with_text(text, top_k=10)
        else:
            results = []

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
            lbl = ClickableLabel()
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if os.path.exists(img_path):
                orig_pix = QPixmap(img_path)
                # 存储原图以便点击时放大
                lbl._orig_pix = orig_pix
                # 缩略图展示：固定 400×400 区域，按比例缩放
                thumb = orig_pix.scaled(
                    400, 400,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                lbl.setPixmap(thumb)
                # 连接点击信号，弹出新窗口
                lbl.clicked.connect(lambda p=orig_pix: self.show_popup(p))
            else:
                lbl.setText(f"无效路径: {img_path}")
            self.results_layout.addWidget(lbl)

    def show_popup(self, pixmap: QPixmap):
        # 弹出一个新的对话框，显示原始大图
        popup = ImagePopup(pixmap, self)
        popup.resize(960, 720)
        popup.show()