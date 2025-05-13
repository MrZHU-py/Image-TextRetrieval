'''
FilePath: \Image-TextRetrieval\tools\index_wiki.py
Author: ZPY
TODO: 
'''
import sys, os
import json
import torch
from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch, helpers
from concurrent.futures import ThreadPoolExecutor, as_completed

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

## 独立配置
ES_HOST = "localhost"
ES_PORT = 9200
TEXT_INDEX = "text_index"
TEXT_DIM = 768
M3E_MODEL_NAME = "moka-ai/m3e-base"

## 1. 自动选择设备并加载 M3E 模型
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
m3e_model = SentenceTransformer(M3E_MODEL_NAME, device=device)
m3e_model.eval()

# 2. ES 客户端 & 索引名
es = Elasticsearch([{"host": ES_HOST, "port": ES_PORT, "scheme": "http"}])
INDEX = TEXT_INDEX

def collect_all_files(data_dir):
    """收集所有文件路径"""
    all_files = []
    for root, _, files in os.walk(data_dir):
        for fname in files:
            path = os.path.join(root, fname)
            all_files.append(path)
    return all_files

def process_and_index(files, batch_size=100):
    """
    处理文件并建立索引。
    本函数读取文件列表中的文件，处理每个文件的内容，并将处理后的数据批量添加到指定的索引中。
    """
    # 初始化操作列表和计数器
    actions = []
    total = 0
    
    for idx, path in enumerate(files):
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip() # 移除行两端的空白字符
                    if not line:    # 跳过空行
                        continue
                    try:
                        rec = json.loads(line)  # 解析 JSON 行
                        if not isinstance(rec, dict):   # 检查是否为字典
                            continue
                        text = rec.get("text", "")  # 获取文本内容
                        if not isinstance(text, str):
                            text = str(text)
                        if len(text) > 300: # 如果文本超过300个字符，则截断并添加省略号
                            text = text[:300] + "…"
                        url = rec.get("url", "")
                        try:
                            # 生成文本嵌入向量
                            emb = m3e_model.encode(text, normalize_embeddings=True).tolist()
                        except Exception as e:
                            # 处理向量生成失败的情况
                            print(f"向量生成失败: {e}")
                            continue
                        # 准备操作列表以进行批量索引
                        actions.append({
                            "_index": TEXT_INDEX,
                            "_source": {
                                "content": text,
                                "url": url,
                                "embedding": emb
                            }
                        })
                        # 当操作列表达到批处理大小时，执行批量索引
                        if len(actions) >= batch_size:
                            helpers.bulk(client=es, actions=actions, chunk_size=200, raise_on_error=False)
                            total += len(actions)
                            print(f"已写入 {total} 条")
                            actions = []
                    except Exception as e:
                        # 处理无效行
                        print(f"跳过无效行 {path}: {e}")
        except Exception as e:
            # 处理无法读取文件的情况
            print(f"跳过文件 {path}: {e}")
    # 处理剩余的操作列表
    if actions:
        helpers.bulk(client=es, actions=actions, chunk_size=200, raise_on_error=False)
        total += len(actions)
        print(f"已写入 {total} 条")
    # 完成处理，输出总记录数
    print(f"全部完成，共写入文档数: {total}")

if __name__ == "__main__":
    data_dir = r"C:\Users\Mr.Zhu\Desktop\wiki_zh_2019\wiki_zh"
    files = collect_all_files(data_dir)
    process_and_index(files, batch_size=100)