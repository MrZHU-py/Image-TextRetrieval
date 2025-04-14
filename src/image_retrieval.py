'''
FilePath: \Image-TextRetrieval\src\image_retrieval.py
Author: ZPY
TODO: 
'''
import os
import torch
from transformers import CLIPProcessor, CLIPModel
from elasticsearch import Elasticsearch
import config
from PIL import Image
import hashlib
import shutil
import csv

# 初始化 Elasticsearch
es = Elasticsearch([{'host': config.ELASTICSEARCH_HOST, 'port': config.ELASTICSEARCH_PORT, 'scheme': 'http'}])

# 加载预训练的 CLIP 模型
device = "cuda" if torch.cuda.is_available() else "cpu"
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def extract_text_features(text):
    """使用 CLIP 提取文本特征向量"""
    try:
        inputs = clip_processor(text=[text], return_tensors="pt", padding=True, truncation=True).to(device)
        with torch.no_grad():
            text_features = clip_model.get_text_features(**inputs)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        return text_features.cpu().numpy().squeeze()
    except Exception as e:
        print(f"Error extracting text features: {e}")
        raise

def extract_image_features(image_path):
    """使用 CLIP 提取图像特征向量"""
    try:
        inputs = clip_processor(images=Image.open(image_path), return_tensors="pt").to(device)
        with torch.no_grad():
            image_features = clip_model.get_image_features(**inputs)
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        return image_features.cpu().numpy().squeeze()
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
def search_image(image_path, top_k=10):
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
def search_image_with_clip(image_path, top_k=10):
    """在 Elasticsearch 中使用 CLIP 特征进行图像相似性搜索"""
    try:
        query_features = extract_image_features(image_path).tolist()
        response = es.search(
            index=config.IMAGE_CLIP_INDEX,
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
        return response['hits']['hits']
    except Exception as e:
        print(f"Error in search_image_with_clip: {e}")
        return []

def load_captions(captions_file):
    """加载 captions.csv 文件"""
    captions = {}
    with open(captions_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            image_id = row["image_id"]
            caption = row["caption"]
            if image_id not in captions:
                captions[image_id] = []
            captions[image_id].append(caption)
    return captions

def search_text_with_image(image_path, top_k=10):
    """根据图像检索相关文本"""
    try:
        # 提取图像特征
        image_features = extract_image_features(image_path).tolist()

        # 构造 Elasticsearch 查询
        query = {
            "size": top_k,
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'text_features') + 1.0",
                        "params": {"query_vector": image_features}
                    }
                }
            }
        }

        # 在 text_clip_index 中执行检索
        response = es.search(index="text_clip_index", body=query)
        return response['hits']['hits']
    except Exception as e:
        print(f"Error in search_text_with_image: {e}")
        return []

def search_image_with_text(query_text, top_k=10):
    """根据文本检索相关图像"""
    text_features = extract_text_features(query_text).tolist()
    response = es.search(
        index="cross_modal_index",
        body={
            "size": top_k,
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'image_features') + 1.0",
                        "params": {"query_vector": text_features}
                    }
                }
            }
        }
    )
    return response['hits']['hits']
