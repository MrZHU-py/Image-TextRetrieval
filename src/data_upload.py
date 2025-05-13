'''
FilePath: \Image-TextRetrieval\src\data_upload.py
Author: ZPY
TODO: 
'''
import os
from PyQt6.QtWidgets import QMessageBox
from config import TEXT_CLIP_INDEX, TEXT_INDEX, es_client
from src.image_retrieval import (
    calculate_image_hash, index_image_with_clip
)
import numpy as np

es = es_client

def check_es_connection():
    try:
        if not es.ping():
            QMessageBox.critical(None, "Elasticsearch错误", "无法连接到Elasticsearch，请检查服务是否启动。")
            return False
        return True
    except Exception as e:
        QMessageBox.critical(None, "Elasticsearch错误", f"连接Elasticsearch失败：{e}")
        return False

def upload_single_image(image_path):
    if not check_es_connection():
        return None
    # 直接调用 image_retrieval 的索引函数
    index_image_with_clip(image_path)
    # 返回图片hash
    return calculate_image_hash(image_path)

def upload_images(image_paths):
    return [upload_single_image(p) for p in image_paths]

def upload_folder_images(folder_path):
    image_paths = []
    for fname in os.listdir(folder_path):
        if fname.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_paths.append(os.path.join(folder_path, fname))
    return upload_images(image_paths)

# 文本相关函数保持不变
def extract_clip_text_feature(text):
    from config import clip_processor, clip_model
    try:
        import torch
        inputs = clip_processor(text=[text], return_tensors="pt", padding=True, truncation=True).to("cpu")
        with torch.no_grad():
            text_features = clip_model.get_text_features(**inputs)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        return text_features.cpu().numpy().squeeze().tolist()
    except Exception as e:
        print(f"extract_clip_text_feature error: {e}")
        return None

def extract_m3e_feature(text):
    from config import m3e_model
    try:
        emb = m3e_model.encode(text)
        emb = emb / np.linalg.norm(emb)
        return emb.tolist()
    except Exception as e:
        print(f"extract_m3e_feature error: {e}")
        return None

def upload_text_annotation(text):
    if not check_es_connection():
        return
    feature = extract_clip_text_feature(text)
    if feature is None:
        return
    doc = {
        "text": text,
        "text_features": feature
    }
    es.index(index=TEXT_CLIP_INDEX, document=doc)

def upload_text(text):
    if not check_es_connection():
        return
    feature = extract_m3e_feature(text)
    if feature is None:
        return
    doc = {
        "content": text,
        "embedding": feature
    }
    es.index(index=TEXT_INDEX, document=doc)

def upload_text_file(file_path, is_annotation=False):
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if is_annotation:
                upload_text_annotation(line)
            else:
                upload_text(line)