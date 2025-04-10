'''
FilePath: \\Image-TextRetrieval\\create_index.py
Author: ZPY
TODO: 
'''
from elasticsearch import Elasticsearch
import config

es = Elasticsearch([{'host': config.ELASTICSEARCH_HOST, 'port': config.ELASTICSEARCH_PORT, 'scheme': 'http'}])

def create_index():
    """ 创建支持向量搜索的索引 """
    index_config = {
        "mappings": {
            "properties": {
                "content": {"type": "text"},
                "embedding": {"type": "dense_vector", "dims": 384}  # SBERT 嵌入维度
            }
        }
    }
    es.indices.create(index=config.ELASTICSEARCH_INDEX, body=index_config, ignore=400)

if __name__ == "__main__":
    create_index()curl -X DELETE "http://localhost:9200/_all"

