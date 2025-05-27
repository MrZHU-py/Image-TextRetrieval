'''
FilePath: \\Image-TextRetrieval\\tools\\del_content.py
Author: ZPY
TODO: 
'''
#!/usr/bin/env python3
import sys
import argparse
from elasticsearch import Elasticsearch

# —— 可根据实际环境修改 —— #
ES_HOST = "localhost"
ES_PORT = 9200
INDEX_NAME = "text_index"
# ———————————————————————— #

def parse_args():
    parser = argparse.ArgumentParser(
        description="Delete documents from Elasticsearch where `content` matches given text"
    )
    parser.add_argument(
        "text", help="要删除的数据片段，将用于精确、短语和通配符匹配"
    )
    parser.add_argument(
        "--host", default=ES_HOST, help="Elasticsearch 主机，默认为 localhost"
    )
    parser.add_argument(
        "--port", type=int, default=ES_PORT, help="Elasticsearch 端口，默认为 9200"
    )
    parser.add_argument(
        "--index", default=INDEX_NAME, help="目标索引，默认为 text_index"
    )
    return parser.parse_args()

def build_query(text):
    # term 查询需使用未分词字段（.keyword）做精确匹配
    return {
        "query": {
            "bool": {
                "should": [
                    {"term": {"content.keyword": {"value": text}}},
                    {"match_phrase": {"content": text}},
                    {"wildcard": {"content": f"*{text}*"}}
                ]
            }
        }
    }

def main():
    args = parse_args()
    es = Elasticsearch([{"host": args.host, "port": args.port, "scheme": "http"}])

    query_body = build_query(args.text)
    # slices="auto" 自动并行切片，提升大数据量删除速度:contentReference[oaicite:2]{index=2}
    response = es.delete_by_query(
        index=args.index,
        body=query_body,
        refresh=True,
        slices="auto",
        wait_for_completion=True
    )
    deleted = response.get("deleted", 0)
    print(f"已删除文档数：{deleted}")

if __name__ == "__main__":
    main()
