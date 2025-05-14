'''
FilePath: \Image-TextRetrieval\tools\del_caption.py
Author: ZPY
TODO: 
'''
from elasticsearch import Elasticsearch
import sys

# 初始化 Elasticsearch 客户端
es = Elasticsearch([{
    'host': 'localhost',
    'port': 9200,
    'scheme': 'http'
}])

def delete_caption(text: str):
    """
    删除 text_clip_index 中 text 字段匹配的文档
    """
    index_name = "text_clip_index"
    query = {
        "query": {
            "match_phrase": {"text": text}
        }
    }
    try:
        resp = es.delete_by_query(index=index_name, body=query, refresh=True)
        deleted = resp.get("deleted", 0)
        print(f"已从 `{index_name}` 删除 {deleted} 条 text = '{text}' 的文档。")
    except Exception as e:
        print(f"删除失败：{e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python del_caption.py <text_to_delete>")
        sys.exit(1)
    _, txt = sys.argv
    delete_caption(txt)