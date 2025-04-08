'''
FilePath: \TextRetrieval\src\search_engine.py
Author: ZPY
TODO: 连接 Elasticsearch，提供索引和搜索功能
'''
from elasticsearch import Elasticsearch
import config

# 连接 Elasticsearch
es = Elasticsearch([{'host': config.ELASTICSEARCH_HOST, 'port': config.ELASTICSEARCH_PORT, 'scheme': 'http'}])

def index_text(text, doc_id):
    """ 索引文本到 Elasticsearch """
    doc = {"content": text}
    es.index(index=config.ELASTICSEARCH_INDEX, id=doc_id, body=doc)

def search_text(query):
    """ 在 Elasticsearch 中搜索文本 """
    response = es.search(index=config.ELASTICSEARCH_INDEX, body={"query": {"match": {"content": query}}})
    return response['hits']['hits']
