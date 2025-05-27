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
    """基于 M3E 模型创建专用的text_index索引，特征值768维度"""
    index_config = {
        "mappings": {
            "properties": {
                "url": {"type": "keyword"},  # URL 字段
                "content": {"type": "text"},
                "embedding": {"type": "dense_vector", "dims": config.TEXT_DIM}
            }
        }
    }
    try:
        if not es.indices.exists(index=config.TEXT_INDEX):
            es.indices.create(index=config.TEXT_INDEX, body=index_config)
            print("Text index created successfully.")
        else:
            print("Text index already exists. Skipping creation.")
    except Exception as e:
        print(f"Error creating text index: {e}")
def create_image_clip_index():
    """创建 CLIP 图像索引，特征值512维度"""
    index_config = {
        "mappings": {
            "properties": {
                "features": {"type": "dense_vector", "dims": config.CLIP_DIM}  # 使用配置中的 CLIP 特征维度
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

def create_text_clip_index():
    """创建 text_clip_index 索引"""
    index_config = {
        "mappings": {
            "properties": {
                "text": {"type": "text"},  # 文本内容
                "text_features": {"type": "dense_vector", "dims": config.CLIP_DIM}  # CLIP 文本特征
            }
        }
    }
    try:
        if not es.indices.exists(index=config.TEXT_CLIP_INDEX):
            es.indices.create(index=config.TEXT_CLIP_INDEX, body=index_config)
            print("text_clip_index created successfully.")
        else:
            print("text_clip_index already exists.")
    except Exception as e:
        print(f"Error creating text_clip_index: {e}")

def delete_index(index_name):
    """删除指定的 Elasticsearch 索引"""
    try:
        if es.indices.exists(index=index_name):
            es.indices.delete(index=index_name)
            print(f"Deleted index: {index_name}")
        else:
            print(f"Index {index_name} does not exist.")
    except Exception as e:
        print(f"Error deleting index {index_name}: {e}")

def initialize_indices():
    """初始化所有索引"""
    create_text_index()
    create_image_clip_index()
    create_text_clip_index()

if __name__ == "__main__":
    # delete_index(config.TEXT_INDEX)
    initialize_indices()