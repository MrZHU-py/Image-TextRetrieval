'''
FilePath: \Image-TextRetrieval\src\gui.py
Author: ZPY
TODO: 用户图像界面交互
'''
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QApplication
from PyQt6.QtGui import QIcon
from config import ICON_DIR
from src.pages.main_page import MainPage
from src.pages.text_search_page import TextSearchPage
from src.pages.image_search_page import ImageSearchPage
from src.pages.text_to_image_page import TextToImagePage
from src.pages.image_to_text_page import ImageToTextPage
from src.pages.upload_page import UploadPage   # 新增

class ImageTextRetrievalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_thread = None
        self.loading_page = None

        # 创建菜单栏
        self.init_menu()

        # 创建 QStackedWidget 管理所有页面
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # 预先创建所有页面
        self.main_page = MainPage()
        self.text_search_page = TextSearchPage()
        self.image_search_page = ImageSearchPage()
        self.text_to_image_page = TextToImagePage()
        self.image_to_text_page = ImageToTextPage()
        self.upload_page = UploadPage()  # 新增

        # 添加页面到stacked_widget
        self.stacked_widget.addWidget(self.main_page)           # index 0
        self.stacked_widget.addWidget(self.text_search_page)    # index 1
        self.stacked_widget.addWidget(self.image_search_page)   # index 2
        self.stacked_widget.addWidget(self.text_to_image_page)  # index 3
        self.stacked_widget.addWidget(self.image_to_text_page)  # index 4
        self.stacked_widget.addWidget(self.upload_page)         # index 5 新增

        # 连接主页面按钮信号
        self.main_page.switch_requested.connect(self.switch_page)

        # 初始化窗口
        self.init_ui()

    def init_menu(self):
        menu_bar = self.menuBar()
        mode_menu = menu_bar.addMenu("菜单")
        # 添加菜单选项
        main_action = mode_menu.addAction("主页面")
        text_search_action = mode_menu.addAction("文搜文")
        image_search_action = mode_menu.addAction("图搜图")
        text_to_image_action = mode_menu.addAction("文搜图")
        image_to_text_action = mode_menu.addAction("图搜文")
        # 绑定菜单选项的事件
        main_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        text_search_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        image_search_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        text_to_image_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        image_to_text_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(4))

    def init_ui(self):
        self.setWindowTitle("Image-Text Retrieval 基于图像的文本检索系统")
        self.setGeometry(100, 100, 1000, 700)
        # 设置窗口图标
        self.setWindowIcon(QIcon(ICON_DIR + "/csuft_logo.jpg"))

    def switch_page(self, index):
        # index: 1=文搜文, 2=图搜图, 3=文搜图, 4=图搜文, 5=上传数据
        if index == 0:
            self.stacked_widget.setCurrentIndex(0)  # 主页面
        elif index == 1:
            self.stacked_widget.setCurrentIndex(1)
        elif index == 2:
            self.stacked_widget.setCurrentIndex(2)
        elif index == 3:
            self.stacked_widget.setCurrentIndex(3)
        elif index == 4:
            self.stacked_widget.setCurrentIndex(4)  # 图搜文页面
        elif index == 5:
            self.stacked_widget.setCurrentIndex(5)  # 上传数据页面

    def closeEvent(self, event):
        if self.init_thread and self.init_thread.isRunning():
            self.init_thread.quit()
            self.init_thread.wait()
        super().closeEvent(event)

def main():
    import sys
    app = QApplication(sys.argv)
    ex = ImageTextRetrievalApp()
    ex.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()