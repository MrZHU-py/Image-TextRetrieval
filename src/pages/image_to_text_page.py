'''
FilePath: \\Image-TextRetrieval\\src\\pages\\image_to_text_page.py
Author: ZPY
TODO: 快速检索页面
'''
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QScrollArea, QSizePolicy, QSpacerItem
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal
from src.image_retrieval import search_text_with_image

class ImageToTextPage(QWidget):
    switch_back = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.pixmap = None            # 用于保存原始 QPixmap
        self.original_texts = []      # 保存原始检索到的文本
        self.initUI()

    def initUI(self):
        """初始化界面布局（自适应、等比例缩放）"""
        # 主布局：水平布局
        main_layout = QHBoxLayout(self)

        # 左侧布局：上传图片和显示区域
        left_layout = QVBoxLayout()

        # 返回按钮
        back_btn = QPushButton("← 返回")
        back_btn.setFixedSize(100, 30)
        back_btn.clicked.connect(self.switch_back.emit)
        left_layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        # 图片展示区域：不让 QLabel 因 pixmap 改变自身 sizeHint
        self.image_label = QLabel("未上传图片")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid black;")
        # 【关键】设为 Ignored，布局只按外部分配给它的空间，而不参考它的 sizeHint
        self.image_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        # 如果需要最小可视面积，可选地设置：
        # self.image_label.setMinimumSize(200, 200)
        left_layout.addWidget(self.image_label, stretch=1)

        # 上传按钮
        self.upload_btn = QPushButton("上传图片", self)
        self.upload_btn.clicked.connect(self.upload_image)
        left_layout.addWidget(self.upload_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # 填充使左侧布局推到顶部
        left_layout.addSpacerItem(QSpacerItem(
            20, 20,
            QSizePolicy.Policy.Minimum,
            QSizePolicy.Policy.Expanding
        ))

        main_layout.addLayout(left_layout, stretch=1)

        # 右侧布局：检索结果显示区域
        right_layout = QVBoxLayout()
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.scroll_area.setWidget(self.results_container)
        right_layout.addWidget(self.scroll_area, stretch=1)

        main_layout.addLayout(right_layout, stretch=1)

        # 设置主布局
        self.setLayout(main_layout)

    def resizeEvent(self, event):
        """窗口大小变化时，对已加载的 pixmap 做等比例缩放并展示"""
        if self.pixmap:
            scaled = self.pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)
        super().resizeEvent(event)

    def upload_image(self):
        """上传图片并检索相关文本"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "选择图片文件",
                "",
                "图片文件 (*.png *.jpg *.jpeg)"
            )
            if not file_path:
                return

            # 1. 读取原始 QPixmap 并保存
            orig = QPixmap(file_path)
            if orig.isNull():
                return
            self.pixmap = orig

            # 2. 初次缩放：用当前 QLabel 大小做一次等比例缩放并 setPixmap
            scaled = self.pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)

            # 3. 调用检索逻辑
            results = search_text_with_image(file_path, top_k=10)

            # 4. 清空之前的检索结果
            for i in reversed(range(self.results_layout.count())):
                widget = self.results_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

            # 5. 显示检索结果
            self.original_texts = []
            if results:
                for result in results:
                    content = result['_source'].get('text', '无相关文本')
                    score = result.get('_score', 0)
                    result_label = QLabel(f"相关文本: {content}\n相关度: {score:.2f}")
                    result_label.setWordWrap(True)
                    self.results_layout.addWidget(result_label)
                    self.original_texts.append(content)
            else:
                self.results_layout.addWidget(QLabel("未找到相关文本。"))

        except Exception as e:
            print(f"Error in upload_image: {e}")
