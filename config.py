'''
FilePath: \TextRetrieval\config.py
Author: ZPY
TODO: 
'''
import os

# Tesseract OCR 路径
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Elasticsearch 配置
ELASTICSEARCH_HOST = "localhost"
ELASTICSEARCH_PORT = 9200
ELASTICSEARCH_INDEX = "text_retrieval"

# Sentence-BERT 相关
SENTENCE_BERT_MODEL = "paraphrase-MiniLM-L6-v2"

# 目录路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
SRC_DIR = os.path.join(BASE_DIR, "src")

