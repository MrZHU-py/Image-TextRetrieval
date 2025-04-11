'''
FilePath: \\Image-TextRetrieval\\clean_index.py
Author: ZPY
TODO: 
'''
from elasticsearch import Elasticsearch

# 初始化 Elasticsearch 客户端
es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])

def delete_empty_content():
    """删除 content 字段为空或仅包含空格的文档"""
    query = {
        "query": {
            "bool": {
                "should": [
                    { "term": { "content.keyword": "" } },
                    { "wildcard": { "content.keyword": " *" } }
                ]
            }
        }
    }
    response = es.delete_by_query(index="text_index", body=query)
    print(f"Deleted documents with empty content: {response}")

def delete_empty_embedding():
    """删除 embedding 字段为空的文档"""
    query = {
        "query": {
            "bool": {
                "must_not": {
                    "exists": { "field": "embedding" }
                }
            }
        }
    }
    response = es.delete_by_query(index="text_index", body=query)
    print(f"Deleted documents with empty embedding: {response}")

def delete_duplicate_content():
    """删除索引中重复的内容"""
    # 查询重复的 content 值
    query = {
        "size": 0,
        "aggs": {
            "duplicate_contents": {
                "terms": {
                    "field": "content.keyword",
                    "min_doc_count": 2  # 至少出现两次的内容
                }
            }
        }
    }
    response = es.search(index="text_index", body=query)
    buckets = response['aggregations']['duplicate_contents']['buckets']

    # 遍历重复的内容
    for bucket in buckets:
        content_value = bucket['key']
        # 查询所有包含该 content 的文档
        search_query = {
            "query": {
                "term": {
                    "content.keyword": content_value
                }
            }
        }
        search_response = es.search(index="text_index", body=search_query)
        hits = search_response['hits']['hits']

        # 保留第一个文档，删除其余文档
        for hit in hits[1:]:
            es.delete(index="text_index", id=hit['_id'])
            print(f"Deleted duplicate document with ID: {hit['_id']}")

    print("Duplicate content cleaned successfully.")

def clean_index():
    """清理索引中的无效或重复内容"""
    delete_empty_content()
    delete_empty_embedding()
    delete_duplicate_content()
    print("Index cleaned successfully.")

clean_index()