'''
FilePath: \\Image-TextRetrieval\\main.py
Author: ZPY
TODO: 程序主入口，启动 GUI 并自动创建索引
'''
import sys
from PyQt6.QtWidgets import QApplication
from src.gui import ImageTextRetrievalApp
import config
from transformers import AutoProcessor, AutoModelForZeroShotImageClassification
from sentence_transformers import SentenceTransformer

def main():

    # 初始化模型配置
    config.clip_processor = AutoProcessor.from_pretrained(config.CN_CLIP_MODEL)
    config.clip_model = AutoModelForZeroShotImageClassification.from_pretrained(config.CN_CLIP_MODEL).to("cpu")
    config.m3e_model = SentenceTransformer(config.M3E_MODEL)

    # 启动 GUI 应用
    app = QApplication(sys.argv)
    ex = ImageTextRetrievalApp()
    ex.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()

