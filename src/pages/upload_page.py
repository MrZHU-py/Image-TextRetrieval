'''
FilePath: \\Image-TextRetrieval\\src\\pages\\upload_page.py
Author: ZPY
TODO: 
'''
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit, QMessageBox, QRadioButton, QButtonGroup
from src.data_upload import (
    upload_single_image, upload_images, upload_folder_images,
    upload_text_annotation, upload_text, upload_text_file
)

class UploadPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("可直接输入文本...")

        # 文本类型选择
        self.radio_group = QButtonGroup(self)
        self.radio_annotation = QRadioButton("图片标注文本")
        self.radio_normal = QRadioButton("普通文本")
        self.radio_normal.setChecked(True)
        self.radio_group.addButton(self.radio_annotation)
        self.radio_group.addButton(self.radio_normal)
        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.radio_annotation)
        radio_layout.addWidget(self.radio_normal)

        btn_upload_img = QPushButton("上传图片")
        btn_upload_imgs = QPushButton("上传多张图片")
        btn_upload_folder = QPushButton("上传图片文件夹")
        btn_upload_txt = QPushButton("上传txt文本")
        btn_ok = QPushButton("确定")
        btn_cancel = QPushButton("取消")

        btn_upload_img.clicked.connect(self.upload_image)
        btn_upload_imgs.clicked.connect(self.upload_images)
        btn_upload_folder.clicked.connect(self.upload_folder)
        btn_upload_txt.clicked.connect(self.upload_txt)
        btn_ok.clicked.connect(self.upload_text_from_box)
        btn_cancel.clicked.connect(self.close)

        layout.addWidget(QLabel("图片上传"))
        layout.addWidget(btn_upload_img)
        layout.addWidget(btn_upload_imgs)
        layout.addWidget(btn_upload_folder)
        layout.addWidget(QLabel("文本上传"))
        layout.addLayout(radio_layout)
        layout.addWidget(self.text_edit)
        layout.addWidget(btn_upload_txt)
        layout.addWidget(btn_ok)
        layout.addWidget(btn_cancel)
        self.setLayout(layout)

    def upload_image(self):
        file, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Images (*.png *.jpg *.jpeg)")
        if file:
            upload_single_image(file)
            QMessageBox.information(self, "上传成功", f"图片已上传：{file}")

    def upload_images(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择多张图片", "", "Images (*.png *.jpg *.jpeg)")
        if files:
            upload_images(files)
            QMessageBox.information(self, "上传成功", f"共上传{len(files)}张图片")

    def upload_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择图片文件夹")
        if folder:
            count = len(upload_folder_images(folder))
            QMessageBox.information(self, "上传成功", f"文件夹内共上传{count}张图片")

    def upload_txt(self):
        file, _ = QFileDialog.getOpenFileName(self, "选择txt文本", "", "Text Files (*.txt)")
        if file:
            is_anno = self.radio_annotation.isChecked()
            QMessageBox.information(self, "提示", "上传的文本必须是清洗后的纯文本！")
            upload_text_file(file, is_annotation=is_anno)
            QMessageBox.information(self, "上传成功", f"文本文件已上传：{file}")

    def upload_text_from_box(self):
        text = self.text_edit.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "提示", "请输入文本内容")
            return
        is_anno = self.radio_annotation.isChecked()
        if is_anno:
            upload_text_annotation(text)
        else:
            upload_text(text)
        QMessageBox.information(self, "上传成功", "文本已上传")
        self.text_edit.clear()