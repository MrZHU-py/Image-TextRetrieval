'''
FilePath: \\Image-TextRetrieval\\src\\image_retrieval.py
Author: ZPY
TODO: 
'''
import os
import numpy as np
import torch
import torchvision.transforms as transforms
from torchvision import models
from elasticsearch import Elasticsearch
import config
from PIL import Image
import hashlib
import shutil
import clip

# 初始化 Elasticsearch
es = Elasticsearch([{'host': config.ELASTICSEARCH_HOST, 'port': config.ELASTICSEARCH_PORT, 'scheme': 'http'}])

# # 加载预训练的 ResNet 模型
# model = models.resnet50(pretrained=True)
# model = torch.nn.Sequential(*list(model.children())[:-1])  # 去掉最后的分类层
# model.eval()

# 加载 CLIP 模型（用clip模型替代ResNet）
device = "cuda" if torch.cuda.is_available() else "cpu"
clip_model, preprocess = clip.load("ViT-B/32", device=device)

# 图像预处理
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def extract_image_features(image_path):
    """使用 CLIP 提取图像特征向量"""
    try:
        # 预处理图像
        image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)

        # 提取特征
        with torch.no_grad():
            features = clip_model.encode_image(image).cpu().numpy().squeeze()
        print(f"Features extracted for image: {image_path}, Shape: {features.shape}")
        return features
    except Exception as e:
        print(f"Error extracting features for image {image_path}: {e}")
        raise

def calculate_image_hash(image_path):
    """计算图片的哈希值"""
    hasher = hashlib.md5()
    with open(image_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def save_image_to_data_dir(image_path, image_hash):
    """将图片保存到 data 目录，文件名为哈希值"""
    data_dir = config.DATA_DIR
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    new_image_path = os.path.join(data_dir, f"{image_hash}.jpg")
    if not os.path.exists(new_image_path):
        shutil.copy(image_path, new_image_path)
        print(f"Image saved to: {new_image_path}")
    return new_image_path

# 基于 ResNet 的图像索引函数
def index_image(image_path):
    """将图像特征索引到 Elasticsearch"""
    try:
        # 计算图片的哈希值
        image_hash = calculate_image_hash(image_path)

        # 将图片保存到 data 目录
        new_image_path = save_image_to_data_dir(image_path, image_hash)

        # 提取图像特征
        features = extract_image_features(new_image_path).tolist()

        # 插入或更新文档
        doc = {
            "features": features,  # 仅存储特征向量
        }
        es.index(index="image_index", id=image_hash, body=doc)
        print(f"Image indexed successfully: {new_image_path}, Hash: {image_hash}")
    except Exception as e:
        print(f"Error indexing image {image_path}: {e}")

# 基于 ResNet 的图像检索函数
def search_image(image_path, top_k=5):
    """在 Elasticsearch 中进行图像相似性搜索"""
    query_features = extract_image_features(image_path).tolist()
    response = es.search(
        index="image_index",
        body={
            "size": top_k,
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'features') + 1.0",
                        "params": {"query_vector": query_features}
                    }
                }
            }
        }
    )
    results = response['hits']['hits']
    for result in results:
        print(f"Found image with Hash ID: {result['_id']}, Score: {result['_score']}")
    return results

# 基于 CLIP 的图像索引函数
def index_image_with_clip(image_path):
    """将图像特征（CLIP）索引到 Elasticsearch"""
    try:
        # 计算图片的哈希值
        image_hash = calculate_image_hash(image_path)

        # 提取图像特征
        features = extract_image_features(image_path).tolist()

        # 插入或更新文档
        doc = {
            "features": features,  # 仅存储特征向量
        }
        es.index(index=config.IMAGE_CLIP_INDEX, id=image_hash, body=doc)
        print(f"Image indexed successfully (CLIP): {image_path}, Hash: {image_hash}")
    except Exception as e:
        print(f"Error indexing image with CLIP {image_path}: {e}")

# 基于 CLIP 的图像检索函数
def search_image_with_clip(image_path, top_k=5):
    """在 Elasticsearch 中使用 CLIP 特征进行图像相似性搜索"""
    query_features = extract_image_features(image_path).tolist()
    response = es.search(
        index=config.IMAGE_CLIP_INDEX,  # 使用 CLIP 索引
        body={
            "size": top_k,
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'features') + 1.0",
                        "params": {"query_vector": query_features}
                    }
                }
            }
        }
    )
    results = response['hits']['hits']
    for result in results:
        print(f"Found image with Hash ID: {result['_id']}, Score: {result['_score']}")
    return results