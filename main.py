'''
FilePath: \\Image-TextRetrieval\\main.py
Author: ZPY
TODO: 程序主入口，启动 GUI
'''
import sys
from PyQt6.QtWidgets import QApplication
from src.gui import ImageTextRetrievalApp

def main():
    app = QApplication(sys.argv)
    ex = ImageTextRetrievalApp()
    ex.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
