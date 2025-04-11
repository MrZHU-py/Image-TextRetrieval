'''
FilePath: \Image-TextRetrieval\src\image_operations.py
Author: ZPY
TODO: 
'''
import uuid
from src.ocr_engine import extract_text_paddleocr
from src.text_retrieval import index_text, search_text
from src.image_retrieval import calculate_image_hash, save_image_to_data_dir, search_image_with_clip, index_image_with_clip
import os

def handle_text_retrieval(file_path):
    """处理文本检索逻辑"""
    try:
        # OCR 识别
        extracted_text = extract_text_paddleocr(file_path)

        # 索引文本
        doc_id = str(uuid.uuid4())
        index_text(extracted_text, doc_id)

        # 检索文本
        search_results = search_text(extracted_text, top_k=5)

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
        search_results = search_image_with_clip(file_path, top_k=5)

        # 提取检索结果中的哈希值
        hash_ids = [result['_id'] for result in search_results]
        return hash_ids
    except Exception as e:
        print(f"Error in handle_image_retrieval: {e}")
        return []