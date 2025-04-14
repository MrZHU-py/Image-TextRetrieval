'''
FilePath: \Image-TextRetrieval\src\image_operations.py
Author: ZPY
TODO: 
'''
import uuid
import os
from src.ocr_engine import extract_text_paddleocr
from src.text_retrieval import index_text, search_text
from src.image_retrieval import calculate_image_hash, save_image_to_data_dir, search_image_with_clip, index_image_with_clip, extract_text_features
from langdetect import detect
import config
from googletrans import Translator  # 导入翻译模块
from elasticsearch import Elasticsearch
from transformers import CLIPProcessor, CLIPModel
import torch
from PIL import Image

# 初始化翻译器
translator = Translator()

# 初始化 Elasticsearch 客户端
es = Elasticsearch([{'host': config.ELASTICSEARCH_HOST, 'port': config.ELASTICSEARCH_PORT, 'scheme': 'http'}])

# 加载 CLIP 模型
device = "cuda" if torch.cuda.is_available() else "cpu"
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32", use_fast=False)

def handle_text_retrieval(file_path):
    """处理文本检索逻辑"""
    try:
        # OCR 识别
        extracted_text = extract_text_paddleocr(file_path)

        # 索引文本
        doc_id = str(uuid.uuid4())
        index_text(extracted_text, doc_id)

        # 检索文本
        search_results = search_text(extracted_text, top_k=10)

        return extracted_text, search_results
    except Exception as e:
        print(f"Error in handle_text_retrieval: {e}")
        return None, []

def handle_image_retrieval(file_path):
    """处理图像检索逻辑"""
    try:
        # 计算图片哈希值并保存到 data 目录
        image_hash = calculate_image_hash(file_path)
        save_image_to_data_dir(file_path, image_hash)

        # 索引图片特征（使用 CLIP 模型）
        index_image_with_clip(file_path)

        # 检索相似图片（使用 CLIP 模型）
        search_results = search_image_with_clip(file_path, top_k=10)

        # 提取检索结果中的哈希值
        hash_ids = [result['_id'] for result in search_results]
        return hash_ids
    except Exception as e:
        print(f"Error in handle_image_retrieval: {e}")
        return []

def search_image_with_text(query_text, top_k=10):
    """根据文本检索相关图像"""
    try:
        # 检测语言并翻译为英文
        if detect(query_text) == "zh-cn":
            query_text = translator.translate(query_text, src="zh-cn", dest="en").text

        text_features = extract_text_features(query_text).tolist()
        response = es.search(
            index=config.CROSS_MODAL_INDEX,  # 使用跨模态索引
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
    except Exception as e:
        print(f"Error in search_image_with_text: {e}")
        return []

def extract_image_features(image_path):
    """提取图片的 CLIP 特征"""
    try:
        image = Image.open(image_path).convert("RGB")
        inputs = clip_processor(images=image, return_tensors="pt").to(device)
        with torch.no_grad():
            image_features = clip_model.get_image_features(**inputs)
        image_features = (image_features / image_features.norm(dim=-1, keepdim=True)).cpu().numpy().squeeze()
        return image_features
    except Exception as e:
        print(f"提取图片特征时出错: {e}")
        return None

def search_text_with_image(image_path, top_k=10):
    """根据图片检索相关文本"""
    try:
        # 提取图片特征
        image_features = extract_image_features(image_path)
        if image_features is None:
            return []

        # 在 text_clip_index 中基于图片特征检索文本
        query = {
            "size": top_k,
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                        "params": {"query_vector": image_features.tolist()}
                    }
                }
            }
        }

        response = es.search(index="text_clip_index", body=query)
        results = response['hits']['hits']
        return results
    except Exception as e:
        print(f"Error in search_text_with_image: {e}")
        return []