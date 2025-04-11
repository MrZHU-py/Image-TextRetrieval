'''
FilePath: \\Image-TextRetrieval\\src\\gui.py
Author: ZPY
TODO: 使用 QStackedWidget 管理界面，修复界面叠加问题
'''
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QApplication
import sys
from src.pages.text_search_page import TextSearchPage
from src.pages.image_search_page import ImageSearchPage
from src.pages.empty_page import EmptyPage

class ImageTextRetrievalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Image-Text Retrieval 基于图像的文本检索系统")
        self.setGeometry(100, 100, 800, 600)

        # 创建菜单栏
        menu_bar = self.menuBar()
        mode_menu = menu_bar.addMenu("模式")

        # 添加菜单选项
        text_search_action = mode_menu.addAction("文搜文")
        image_search_action = mode_menu.addAction("图搜图")
        text_to_image_action = mode_menu.addAction("文搜图")
        image_to_text_action = mode_menu.addAction("图搜文")

        # 绑定菜单选项的事件
        text_search_action.triggered.connect(lambda: self.switch_page(0))
        image_search_action.triggered.connect(lambda: self.switch_page(1))
        text_to_image_action.triggered.connect(lambda: self.switch_page(2))
        image_to_text_action.triggered.connect(lambda: self.switch_page(3))

        # 创建 QStackedWidget
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # 添加页面
        self.stacked_widget.addWidget(TextSearchPage())  # 文搜文页面
        self.stacked_widget.addWidget(ImageSearchPage())  # 图搜图页面
        self.stacked_widget.addWidget(EmptyPage("文搜图功能暂未实现"))  # 文搜图页面
        self.stacked_widget.addWidget(EmptyPage("图搜文功能暂未实现"))  # 图搜文页面

    def switch_page(self, index):
        """切换 QStackedWidget 的页面"""
        self.stacked_widget.setCurrentIndex(index)

def main():
    app = QApplication(sys.argv)
    ex = ImageTextRetrievalApp()
    ex.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()