'''
FilePath: \Image-TextRetrieval\src\search_engine.py
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
    """ 索引文本到 Elasticsearch """
    # 生成文本嵌入
    embedding = model.encode(text).tolist()
    doc = {
        "content": text,
        "embedding": embedding  # 存储嵌入向量
    }
    es.index(index=config.ELASTICSEARCH_INDEX, id=doc_id, body=doc)

def search_text(query, top_k=10):
    """ 在 Elasticsearch 中进行语义搜索 """
    # 生成查询文本的嵌入
    query_embedding = model.encode(query).tolist()
    # 构造向量搜索的查询
    response = es.search(
        index=config.ELASTICSEARCH_INDEX,
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