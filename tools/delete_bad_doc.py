'''
FilePath: \Image-TextRetrieval\tools\delete_bad_doc.py
Author: ZPY
TODO: 
'''
from elasticsearch import Elasticsearch

def delete_docs_missing_content():
    # 初始化 Elasticsearch 客户端
    es = Elasticsearch([{
        'host': 'localhost',
        'port': 9200,
        'scheme': 'http'
    }])

    # 先查询一下将要删除的文档（可选，帮助确认）
    preview = es.search(
        index="text_index",
        body={
            "_source": ["_id", "text", "url", "content"],
            "size": 5,
            "query": {
                "bool": {
                    "must_not": [
                        { "exists": { "field": "content" } },
                        { "term":   { "content.keyword": "" } }
                    ]
                }
            }
        }
    )
    print("预览将被删除的文档（最多 5 条）：")
    for hit in preview['hits']['hits']:
        print(f"  id={hit['_id']}  text={hit['_source'].get('text')}")

    # 真正执行删除
    resp = es.delete_by_query(
        index="text_index",
        body={
            "query": {
                "bool": {
                    "must_not": [
                        { "exists": { "field": "content" } },
                        { "term":   { "content.keyword": "" } }
                    ]
                }
            }
        },
        refresh=True  # 确保立即生效
    )
    print(f"已删除文档总数：{resp.get('deleted')}")

if __name__ == "__main__":
    delete_docs_missing_content()
