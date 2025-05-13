'''
FilePath: \Image-TextRetrieval\src\image_retrieval.py
Author: ZPY
TODO: 
'''
import os
import torch
from PIL import Image
import hashlib
import shutil
import config
from config import es_client as es  # 使用配置文件中的 ES 实例

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

def index_image_with_clip(image_path):
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
