'''
FilePath: \\Image-TextRetrieval\\src\\pages\\upload_page.py
Author: ZPY
TODO: 上传数据界面（仅支持图片及图片标注文本上传）
'''
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from src.data_upload import (
    upload_single_image, upload_images, upload_folder_images,
    upload_text_annotation, upload_text_file
)
import os

class UploadPage(QWidget):
    switch_back = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 返回按钮
        back_btn = QPushButton("← 返回")
        back_btn.setFixedSize(100, 30)
        back_btn.clicked.connect(self.switch_back.emit)
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addSpacing(20)

        # 图片上传区
        layout.addWidget(QLabel("图片上传："))
        btn_upload_img = QPushButton("上传单张图片")
        btn_upload_img.clicked.connect(self.upload_image)
        btn_upload_imgs = QPushButton("上传多张图片")
        btn_upload_imgs.clicked.connect(self.upload_images)
        btn_upload_folder = QPushButton("上传图片文件夹")
        btn_upload_folder.clicked.connect(self.upload_folder)
        layout.addWidget(btn_upload_img)
        layout.addWidget(btn_upload_imgs)
        layout.addWidget(btn_upload_folder)
        layout.addSpacing(30)

        # 标注文本上传区
        layout.addWidget(QLabel("图片标注文本上传："))
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("请输入图片标注文本，用于快速检索...")
        layout.addWidget(self.text_edit)
        btn_upload_text = QPushButton("上传标注文本")
        btn_upload_text.clicked.connect(self.upload_annotation_text)
        layout.addWidget(btn_upload_text)
        layout.addSpacing(30)

        # 文本文件上传区
        layout.addWidget(QLabel("标注文本文件上传(txt)："))
        btn_txt_file = QPushButton("上传文本文件")
        btn_txt_file.clicked.connect(self.upload_txt_file)
        layout.addWidget(btn_txt_file)

        btn_txt_folder = QPushButton("上传文本文件夹")
        btn_txt_folder.clicked.connect(self.upload_txt_folder)
        layout.addWidget(btn_txt_folder)

        layout.addStretch(1)
        self.setLayout(layout)

    def upload_image(self):
        file, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "图片 (*.png *.jpg *.jpeg)")
        if file:
            try:
                upload_single_image(file)
                QMessageBox.information(self, "上传成功", f"图片已上传：{file}")
            except Exception as e:
                QMessageBox.critical(self, "上传失败", f"图片上传失败：{e}")

    def upload_images(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择多张图片", "", "图片 (*.png *.jpg *.jpeg)")
        if files:
            try:
                upload_images(files)
                QMessageBox.information(self, "上传成功", f"共上传 {len(files)} 张图片")
            except Exception as e:
                QMessageBox.critical(self, "上传失败", f"批量上传失败：{e}")

    def upload_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择图片文件夹")
        if folder:
            try:
                count = upload_folder_images(folder)
                QMessageBox.information(self, "上传成功", f"文件夹内共上传 {count} 张图片")
            except Exception as e:
                QMessageBox.critical(self, "上传失败", f"文件夹上传失败：{e}")

    def upload_annotation_text(self):
        text = self.text_edit.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "提示", "请输入标注文本后再上传！")
            return
        try:
            upload_text_annotation(text)
            QMessageBox.information(self, "上传成功", "标注文本已上传！")
            self.text_edit.clear()
        except Exception as e:
            QMessageBox.critical(self, "上传失败", f"文本上传失败：{e}")

    def upload_txt_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "选择txt文本", "", "Text Files (*.txt)")
        if not file:
            return
        # 提示确认
        ret = QMessageBox.question(
            self,
            "确认上传",
            "请确保该文件为纯文本，每行为一条标注文本，继续上传？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if ret != QMessageBox.StandardButton.Yes:
            return
        try:
            upload_text_file(file, is_annotation=True)
            QMessageBox.information(self, "上传成功", f"文本文件已上传：{file}")
        except Exception as e:
            QMessageBox.critical(self, "上传失败", f"文件上传失败：{e}")

    def upload_txt_folder(self):
        # 先选择模式
        msg = QMessageBox(self)
        msg.setWindowTitle("选择上传模式")
        msg.setText("请选择文件夹上传模式：")
        btn_file = msg.addButton("每个文件一条", QMessageBox.ButtonRole.ActionRole)
        btn_line = msg.addButton("每行一条", QMessageBox.ButtonRole.ActionRole)
        msg.addButton(QMessageBox.StandardButton.Cancel)
        msg.exec()
        mode = None
        if msg.clickedButton() == btn_file:
            mode = 'file'
        elif msg.clickedButton() == btn_line:
            mode = 'line'
        else:
            return

        # 用户选择模式后再选择文件夹
        folder = QFileDialog.getExistingDirectory(self, "选择文本文件夹")
        if not folder:
            return

        # 遍历txt
        count = 0
        for fname in os.listdir(folder):
            if not fname.lower().endswith('.txt'):
                continue
            path = os.path.join(folder, fname)
            try:
                if mode == 'file':
                    upload_text_file(path, is_annotation=True)
                    count += 1
                else:
                    # 每行一条
                    with open(path, 'r', encoding='utf-8') as f:
                        for line in f:
                            text = line.strip()
                            if text:
                                upload_text_annotation(text)
                                count += 1
            except Exception:
                continue
        QMessageBox.information(self, "上传完成", f"共上传 {count} 条标注文本")