'''
FilePath: \\Image-TextRetrieval\\src\\text_retrieval.py
Author: ZPY
TODO: 连接 Elasticsearch，提供索引和搜索功能
'''
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
import config
import hashlib
import numpy as np

# 初始化 Elasticsearch
es = Elasticsearch([{'host': config.ELASTICSEARCH_HOST, 'port': config.ELASTICSEARCH_PORT, 'scheme': 'http'}])

# 加载预训练的 Sentence-BERT 模型
model = SentenceTransformer(config.SENTENCE_BERT_MODEL)  # 加载 SBERT 模型

def index_text(text, doc_id):
    """索引文本到 Elasticsearch"""
    try:
        # 校验文本内容是否为空
        if not text.strip():
            print("Text is empty, skipping indexing.")
            return

        # 生成文本嵌入
        embedding = model.encode(text)
        normalized_embedding = (embedding / np.linalg.norm(embedding)).tolist()  # 对 SBERT 生成的嵌入向量进行归一化，以消除向量模的影响

        # 构建文档并索引到 Elasticsearch
        doc = {
            "content": text,
            "embedding": normalized_embedding
        }
        es.index(index="text_index", id=doc_id, body=doc)
        print(f"Indexed document with ID: {doc_id}")
    except Exception as e:
        print(f"Error in index_text: {e}")

def search_text(query, top_k=5):
    """在 Elasticsearch 中进行文本检索"""
    try:
        # 确保查询为字符串
        if not isinstance(query, str):
            raise ValueError("Query must be a string.")

        # 生成查询嵌入
        query_embedding = model.encode(query)
        normalized_query_embedding = (query_embedding / np.linalg.norm(query_embedding)).tolist()  # 归一化

        # 在 Elasticsearch 中执行检索
        response = es.search(
            index="text_index",
            body={
                "size": top_k,
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"content": query}}  # 关键词匹配
                        ],
                        "should": [
                            {
                                "script_score": {
                                    "query": {"match_all": {}},
                                    "script": {
                                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                                        "params": {"query_vector": normalized_query_embedding}
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        )
        return response['hits']['hits']
    except Exception as e:
        print(f"Error in search_text: {e}")
        return []