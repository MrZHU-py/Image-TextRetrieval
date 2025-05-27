'''
FilePath: \\Image-TextRetrieval\\src\\image_retrieval.py
Author: ZPY
TODO: 
'''
import os
import numpy as np
import torch
from PIL import Image
import hashlib
import shutil
from src.text_retrieval import search_text               # 文搜文
import config
from config import es_client as es  # 使用配置文件中的 ES 实例
from src.text_retrieval import search_text
from PyQt6.QtWidgets import QMessageBox

# 自动选择 GPU 或 CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

def extract_text_features(text):
    try:
        from config import clip_processor, clip_model  # 放在函数内部
        inputs = clip_processor(text=[text], return_tensors="pt", padding=True, truncation=True).to(device)
        with torch.no_grad():
            text_features = clip_model.get_text_features(**inputs)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        return text_features.cpu().numpy().squeeze()
    except Exception as e:
        print(f"Error extracting text features: {e}")
        return None

def extract_image_features(image_path):
    try:
        from config import clip_processor, clip_model  # 放在函数内部，避免取到空值
        image = Image.open(image_path).convert("RGB")
        inputs = clip_processor(images=image, return_tensors="pt").to(device)
        with torch.no_grad():
            image_features = clip_model.get_image_features(**inputs)
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        return image_features.cpu().numpy().squeeze()
    except Exception as e:
        print(f"Error extracting features for image {image_path}: {e}")
        return None

def calculate_image_hash(image_path):
    hasher = hashlib.md5()
    with open(image_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def save_image_to_data_dir(image_path, image_hash):
    data_dir = config.DATA_DIR
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    ext = os.path.splitext(image_path)[-1]  # 获取原始后缀
    new_image_path = os.path.join(data_dir, f"{image_hash}{ext}")
    if not os.path.exists(new_image_path):
        shutil.copy(image_path, new_image_path)
    return new_image_path

def check_es_connection():
    try:
        if not es.ping():
            QMessageBox.critical(None, "Elasticsearch连接失败", "无法连接到Elasticsearch，请检查服务是否启动。")
            return False
        return True
    except Exception:
        QMessageBox.critical(None, "Elasticsearch连接失败", "无法连接到Elasticsearch，请检查服务是否启动。")
        return False

def index_image_with_clip(image_path):
    if not check_es_connection():
        return
    try:
        image_hash = calculate_image_hash(image_path)
        ext = os.path.splitext(image_path)[-1]
        filename = f"{image_hash}{ext}"
        new_image_path = save_image_to_data_dir(image_path, image_hash)
        features = extract_image_features(new_image_path)
        if features is None:
            return
        doc = {
            "features": features.tolist(),
        }
        # 关键：用 filename 作为 _id
        es.index(index=config.IMAGE_CLIP_INDEX, id=filename, body=doc)
    except Exception as e:
        print(f"Error indexing image with CLIP {image_path}: {e}")

def search_image_with_clip(image_path, top_k=10):
    if not check_es_connection():
        return []
    try:
        query_features = extract_image_features(image_path)
        if query_features is None:
            return []
        script_query = {
            "size": top_k,
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'features') + 1.0",
                        "params": {"query_vector": query_features.tolist()}
                    }
                }
            }
        }

        try:
            response = es.search(
                index=config.IMAGE_CLIP_INDEX,
                body=script_query
            )
            return response['hits']['hits']
        except Exception as e:
            print(f"Elasticsearch search error: {str(e)}")
            return []
            
    except Exception as e:
        print(f"Error in search_image_with_clip: {str(e)}")
        return []

# 图像检索文本
def search_text_with_image(image_path, top_k=10):
    """
    函数从给定的图片中提取特征，然后使用这些特征作为查询向量，
    在Elasticsearch中搜索与之最相关的文本。检索结果按相关度排序。
    """
    if not check_es_connection():
        return []
    try:
        image_features = extract_image_features(image_path) # 提取图像特征
        if image_features is None:
            return []

        # 构建Elasticsearch查询语句
        query = {
            "size": top_k,
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'text_features') + 1.0",
                        "params": {"query_vector": image_features.tolist()}
                    }
                }
            }
        }

        # 执行搜索并返回结果
        response = es.search(index=config.TEXT_CLIP_INDEX, body=query)
        return response['hits']['hits']
    except Exception as e:
        # 捕获并打印搜索过程中可能发生的任何异常
        print(f"Error in search_text_with_image: {e}")
        return []

def search_image_with_text(query_text, top_k=10):
    if not check_es_connection():
        return []
    try:
        text_features = extract_text_features(query_text)
        if text_features is None:
            return []
        response = es.search(
            index=config.IMAGE_CLIP_INDEX,
            body={
                "size": top_k,
                "query": {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'features') + 1.0",
                            "params": {"query_vector": text_features.tolist()}
                        }
                    }
                }
            }
        )
        return response['hits']['hits']
    except Exception as e:
        print(f"Error in search_image_with_text: {e}")
        return []

def search_image_with_clip_and_text(image_path, query_text, top_k=10, img_k=50):
    """
    先用 CLIP 对图像检索 img_k 条候选，再用文本特征对这批候选重新打分并返回 top_k。
    如果在任何一步出错或特征为空，则退而展示纯图像检索的前 top_k。
    """
    # 1. 图像候选
    img_hits = search_image_with_clip(image_path, top_k=img_k)
    if not img_hits:
        return []

    # 2. 文本特征
    text_vec = extract_text_features(query_text)
    if text_vec is None:    # 文本特征失败时直接返回前 top_k 图像结果
        return img_hits[:top_k] 

    # 3. 对每个候选取出它的 features，然后计算文本相似度
    scored = []
    for hit in img_hits:
        src = hit.get('_source', {})
        feat = src.get('features')
        if feat is None:
            continue
        feat_vec = np.array(feat, dtype=np.float32)
        # 归一化后计算余弦相似度
        txt = text_vec / np.linalg.norm(text_vec)
        img = feat_vec / np.linalg.norm(feat_vec)
        cos_sim = float(np.dot(txt, img))
        scored.append((cos_sim, hit))

    if not scored:
        return img_hits[:top_k]

    # 4. 按文本相似度降序，取 top_k
    scored.sort(key=lambda x: x[0], reverse=True)
    return [hit for _, hit in scored[:top_k]]

# 深度检索相关代码
def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """计算两个向量的余弦相似度"""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def dedup_short_texts(short_texts, sim_threshold=0.9):
    """
    输入：短文本列表
    输出：去重后的短文本列表
    """
    reps = []   # 保存已选代表文本
    feats = []  # 对应的特征向量
    for txt in short_texts:
        try:
            f = extract_text_features(txt)
        except Exception:
            continue
        if f is None:
            continue

        # 检查与已有代表的相似度
        if any(cosine_sim(f, rf) > sim_threshold for rf in feats):
            continue
        reps.append(txt)
        feats.append(f)
    return reps

def search_deep_text_with_image(image_path, top_k_clip=10, sim_threshold=0.9):
    """
    深度检索：
      1. 用 CLIP 拿到 top_k_clip 条短文本；
      2. 对短文本去重（相似度 > sim_threshold 视为重复）；
      3. 顺序对每条去重后文本做 M3E 文搜文 top_k=1；
      4. 合并并按 URL/内容去重，返回最终结果列表。
    """
    # 1. 快速检索：拿到与图片相关的标注
    clip_hits = search_text_with_image(image_path, top_k=top_k_clip)
    if not clip_hits:
        return []

    short_texts = [hit['_source'].get('text', '') for hit in clip_hits]
    # 2. 去重
    unique_texts = dedup_short_texts(short_texts, sim_threshold=sim_threshold)
    if not unique_texts:
        return []

    # 3. 顺序二次检索
    long_hits = []
    for txt in unique_texts:
        try:
            hits = search_text(txt, top_k=1)
        except Exception:
            continue
        if hits:
            long_hits.append(hits[0])

    # 4. 最终合并去重
    seen = set()
    final_hits = []
    # 按_score降序
    for hit in sorted(long_hits, key=lambda x: x.get('_score', 0), reverse=True):
        src = hit.get('_source', {})
        key = src.get('url') or src.get('content')
        if key and key not in seen:
            seen.add(key)
            final_hits.append(hit)

    return final_hits
