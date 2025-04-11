'''
FilePath: \\Image-TextRetrieval\\create_index.py
Author: ZPY
TODO: 初始化 Elasticsearch 索引
'''
from elasticsearch import Elasticsearch
import config

# 初始化 Elasticsearch
es = Elasticsearch([{'host': config.ELASTICSEARCH_HOST, 'port': config.ELASTICSEARCH_PORT, 'scheme': 'http'}])

def create_text_index():
    """创建文本索引"""
    index_config = {
        "mappings": {
            "properties": {
                "content": {"type": "text"},
                "embedding": {"type": "dense_vector", "dims": config.TEXT_DIM}
            }
        }
    }
    try:
        if not es.indices.exists(index="text_index"):
            es.indices.create(index="text_index", body=index_config)
            print("Text index created successfully.")
        else:
            print("Text index already exists. Skipping creation.")
    except Exception as e:
        print(f"Error creating text index: {e}")

def create_image_index():
    """创建图像索引，基于 ResNet 模型，特征值2048维度"""
    index_config = {
        "mappings": {
            "properties": {
                "features": {"type": "dense_vector", "dims": config.IMAGE_DIM}
            }
        }
    }
    try:
        if not es.indices.exists(index="image_index"):
            es.indices.create(index="image_index", body=index_config)
            print("Image index created successfully.")
        else:
            print("Image index already exists. Skipping creation.")
    except Exception as e:
        print(f"Error creating image index: {e}")

def create_image_clip_index():
    """创建 CLIP 图像索引，特征值512维度"""
    index_config = {
        "mappings": {
            "properties": {
                "features": {"type": "dense_vector", "dims": config.IMAGE_CLIP_DIM}  # 使用配置中的 CLIP 特征维度
            }
        }
    }
    try:
        if not es.indices.exists(index=config.IMAGE_CLIP_INDEX):
            es.indices.create(index=config.IMAGE_CLIP_INDEX, body=index_config)
            print("CLIP Image index created successfully.")
        else:
            print("CLIP Image index already exists. Skipping creation.")
    except Exception as e:
        print(f"Error creating CLIP image index: {e}")

def initialize_indices():
    """初始化所有索引"""
    create_text_index()
    # create_image_index()  # resnet模型升级为clip模型，暂时不需要resnet索引
    create_image_clip_index()

if __name__ == "__main__":
    initialize_indices()