'''
FilePath: \Image-TextRetrieval\src\text_retrieval.py
Author: ZPY
TODO: 连接 Elasticsearch，提供索引和搜索功能
'''
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
import config

# 初始化 Elasticsearch 和 SBERT 模型
es = Elasticsearch([{'host': config.ELASTICSEARCH_HOST, 'port': config.ELASTICSEARCH_PORT, 'scheme': 'http'}])
model = SentenceTransformer(config.SENTENCE_BERT_MODEL)  # 加载 SBERT 模型

def index_text(text, doc_id):
    """索引文本到 Elasticsearch"""
    embedding = model.encode(text).tolist()
    doc = {
        "content": text,
        "embedding": embedding
    }
    es.index(index="text_index", id=doc_id, body=doc)

def search_text(query, top_k=5):
    """在 Elasticsearch 中进行文本检索"""
    query_embedding = model.encode(query).tolist()
    response = es.search(
        index="text_index",
        body={
            "size": top_k,
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                        "params": {"query_vector": query_embedding}
                    }
                }
            }
        }
    )
    return response['hits']['hits']