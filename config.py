'''
FilePath: \Image-TextRetrieval\config.py
Author: ZPY
TODO: 配置文件：存储全局配置参数
'''
import os
from elasticsearch import Elasticsearch

# Elasticsearch 配置
ELASTICSEARCH_HOST = "localhost"  # Elasticsearch 主机地址
ELASTICSEARCH_PORT = 9200         # Elasticsearch 端口
ELASTICSEARCH_TIMEOUT = 30        # 连接超时时间（秒）

# 创建 ES 客户端实例（添加版本兼容参数）
es_client = Elasticsearch(
    hosts=[f"http://{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}"],
    timeout=ELASTICSEARCH_TIMEOUT,
    # request_timeout=ELASTICSEARCH_TIMEOUT,
    verify_certs=False
)

# 实例化模型
clip_processor = None
clip_model = None
m3e_model = None

# 索引配置
TEXT_INDEX = "text_index"           # M3E 文本索引
IMAGE_INDEX = "image_index"         # ResNet 特征索引
IMAGE_CLIP_INDEX = "image_clip_index"  # CLIP 图像索引
TEXT_CLIP_INDEX = "text_clip_index"    # CLIP 文本索引
CROSS_MODAL_INDEX = "cross_modal_index"  # CLIP 图像和文本跨模态索引

# 模型维度配置
TEXT_DIM = 768    # M3E-base 输出向量维度
IMAGE_DIM = 2048  # ResNet 特征维度
CLIP_DIM = 512    # CLIP 特征维度

# 模型配置
# SENTENCE_BERT_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
# CLIP_MODEL = "openai/clip-vit-base-patch16"  # CLIP 模型路径
M3E_MODEL = "moka-ai/m3e-base"  # M3E 模型路径
CN_CLIP_MODEL = "OFA-Sys/chinese-clip-vit-base-patch16"  # Chinese-CLIP 模型路径

# 文件路径配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "images")  # 图片存储目录
MODELS_DIR = os.path.join(BASE_DIR, "models")        # 模型存储目录
SRC_DIR = os.path.join(BASE_DIR, "src")
ICON_DIR = os.path.join(BASE_DIR, "data", "icons")           # 图标存储目录
TOOLS_DIR = os.path.join(BASE_DIR, "tools")           # 工具存储目录

# Tesseract OCR 路径
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"