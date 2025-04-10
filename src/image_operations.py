import uuid
from src.ocr_engine import extract_text_paddleocr
from src.text_retrieval import index_text, search_text
from src.image_retrieval import search_image, index_image
from src.image_retrieval import calculate_image_hash, index_image, save_image_to_data_dir
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

def handle_text_retrieval(file_path):
    """处理文本检索逻辑"""
    # OCR 识别
    extracted_text = extract_text_paddleocr(file_path)

    # 索引文本
    doc_id = str(uuid.uuid4())
    index_text(extracted_text, doc_id)

    # 检索文本
    search_results = search_text(extracted_text, top_k=5)
    return extracted_text, search_results

def handle_image_retrieval(file_path):
    """处理图像检索逻辑"""
    try:
        # 计算图片哈希值并保存到 data 目录
        image_hash = calculate_image_hash(file_path)
        save_image_to_data_dir(file_path, image_hash)
        # print(f"Image hash: {image_hash}")
        # print(f"Image saved to: {file_path+image_hash}")

        # 索引图片特征
        index_image(file_path)

        # 检索相似图片
        search_results = search_image(file_path, top_k=5)

        # 提取检索结果中的哈希值
        hash_ids = [result['_id'] for result in search_results]
        return hash_ids
    except Exception as e:
        print(f"Error in handle_image_retrieval: {e}")
        return []