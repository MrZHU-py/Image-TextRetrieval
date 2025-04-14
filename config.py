'''
FilePath: \\Image-TextRetrieval\\config.py
Author: ZPY
TODO: 
'''
import os

# Tesseract OCR 路径
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Elasticsearch 配置
ELASTICSEARCH_HOST = "localhost"
ELASTICSEARCH_PORT = 9200

# 索引名称配置
TEXT_INDEX = "text_index"   # SBERT 文本索引
IMAGE_INDEX = "image_index"  # ResNet 特征索引
IMAGE_CLIP_INDEX = "image_clip_index"  # CLIP 图像索引
CROSS_MODAL_INDEX = "cross_modal_index"  # CLIP 图像和文本跨模态索引
TEXT_CLIP_INDEX = "text_clip_index"  # CLIP 中文文本索引

# 索引维度配置
TEXT_DIM = 384  # SBERT 嵌入维度
IMAGE_DIM = 2048  # ResNet 特征维度
CLIP_DIM = 512  # CLIP 特征维度

# Sentence-BERT 模型配置
SENTENCE_BERT_MODEL = "paraphrase-MiniLM-L6-v2"

# 目录路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
SRC_DIR = os.path.join(BASE_DIR, "src")
