'''
FilePath: \Image-TextRetrieval\src\image_operations.py
Author: ZPY
TODO: 
'''
from src.ocr_engine import extract_text_ocr
from src.text_retrieval import search_text
from src.image_retrieval import (
    calculate_image_hash, save_image_to_data_dir,
    search_image_with_clip, index_image_with_clip
)
from src.preprocessing import preprocess_image


def handle_text_retrieval(file_path):
    """处理文本检索逻辑（整图OCR）"""
    try:
        _, processed_img = preprocess_image(file_path)
        extracted_text = extract_text_ocr(processed_img)
        search_results = search_text(extracted_text, top_k=10)
        return extracted_text, search_results
    except Exception as e:
        print(f"Error in handle_text_retrieval: {e}")
        return None, []

def handle_image_retrieval(file_path):
    """处理图像检索逻辑"""
    try:
        image_hash = calculate_image_hash(file_path)
        save_image_to_data_dir(file_path, image_hash)
        index_image_with_clip(file_path)
        search_results = search_image_with_clip(file_path, top_k=10)
        hash_ids = [result['_id'] for result in search_results]
        return hash_ids
    except Exception as e:
        print(f"Error in handle_image_retrieval: {e}")
        return []