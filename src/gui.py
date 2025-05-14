'''
FilePath: \Image-TextRetrieval\src\gui.py
Author: ZPY
TODO: 
'''
'''
FilePath: \Image-TextRetrieval\src\gui.py
Author: ZPY
TODO: 用户图像界面交互
'''
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QApplication, QColorDialog, QFontDialog
from PyQt6.QtGui import QIcon, QAction
from config import ICON_DIR
from src.pages.main_page import MainPage
from src.pages.ocr_search_page import OCRSearchPage
from src.pages.advanced_image_search_page import AdvancedImageSearchPage
from src.pages.image_to_text_page import ImageToTextPage
from src.pages.upload_page import UploadPage   # 新增
from src.pages.deep_search_page import DeepSearchPage  # 深度检索页面（待实现）

class ImageTextRetrievalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_menu()
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # 预创建所有页面
        self.main_page = MainPage()
        self.ocr_search_page = OCRSearchPage()
        self.advanced_image_search_page = AdvancedImageSearchPage()
        self.image_to_text_page = ImageToTextPage()
        self.upload_page = UploadPage()
        self.deep_search_page = DeepSearchPage()

        # 注册所有页面的返回信号
        self.deep_search_page.switch_back.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.ocr_search_page.switch_back.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.advanced_image_search_page.switch_back.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.image_to_text_page.switch_back.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.upload_page.switch_back.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        # 添加页面到堆栈
        pages = [
            self.main_page,
            self.image_to_text_page,
            self.deep_search_page,
            self.ocr_search_page,
            self.advanced_image_search_page,
            self.upload_page,
        ]
        for page in pages:
            self.stacked_widget.addWidget(page)

        # 连接主页面按钮
        self.main_page.switch_requested.connect(self.switch_page)
        self.init_ui()

    def init_menu(self):
        menu_bar = self.menuBar()

        # ‘菜单’：页面切换
        mode_menu = menu_bar.addMenu("菜单")
        labels = [ "主页面", "快速检索", "深度检索", "OCR 检索", "图像检索", "上传数据" ]
        for idx, lbl in enumerate(labels):
            action = QAction(lbl, self)
            action.triggered.connect(lambda _, i=idx: self.stacked_widget.setCurrentIndex(i))
            mode_menu.addAction(action)

        # ‘设置’：只保留字体选项
        settings_menu = menu_bar.addMenu("设置")
        font_action = QAction("字体", self)
        font_action.triggered.connect(self.choose_font)
        settings_menu.addAction(font_action)

    def choose_font(self):
        # 打开字体对话框并应用全局字体
        font, ok = QFontDialog.getFont(self)
        if ok:
            QApplication.instance().setFont(font)

    def init_ui(self):
        self.setWindowTitle("Image-Text Retrieval 系统")
        self.setGeometry(100, 100, 1000, 700)
        self.setWindowIcon(QIcon(ICON_DIR + "/csuft_logo.jpg"))

    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)

    def closeEvent(self, event):
        super().closeEvent(event)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = ImageTextRetrievalApp()
    win.show()
    sys.exit(app.exec())