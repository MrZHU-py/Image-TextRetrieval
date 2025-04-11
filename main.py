'''
FilePath: \Image-TextRetrieval\main.py
Author: ZPY
TODO: 程序主入口，启动 GUI 并自动创建索引
'''
import sys
from PyQt6.QtWidgets import QApplication
from src.gui import ImageTextRetrievalApp
from create_index import initialize_indices  # 导入索引初始化函数

def main():

    # 启动 GUI 应用
    app = QApplication(sys.argv)
    ex = ImageTextRetrievalApp()
    ex.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
