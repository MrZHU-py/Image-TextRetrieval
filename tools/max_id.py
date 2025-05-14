'''
FilePath: \Image-TextRetrieval\tools\max_id.py
Author: ZPY
TODO: 
'''
import os, sys
from elasticsearch import Elasticsearch
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import config
from config import es_client

es = es_client  # 直接使用config.py中创建的es_client实例

def get_max_id(index_name):
    max_id = None
    max_id_int = -1
    try:
        # 使用 scan 遍历所有文档
        resp = es.search(index=index_name, body={"query": {"match_all": {}}}, scroll="2m", size=1000)
        sid = resp['_scroll_id']
        scroll_size = len(resp['hits']['hits'])
        while scroll_size > 0:
            for hit in resp['hits']['hits']:
                try:
                    cur_id = int(hit['_id'])
                    if cur_id > max_id_int:
                        max_id_int = cur_id
                        max_id = hit['_id']
                except Exception:
                    continue
            resp = es.scroll(scroll_id=sid, scroll="2m")
            sid = resp['_scroll_id']
            scroll_size = len(resp['hits']['hits'])
        if max_id is not None:
            print(f"当前text_clip_index中id最大值为: {max_id}")
        else:
            print("未找到任何文档。")
    except Exception as e:
        print(f"查询失败: {e}")

if __name__ == "__main__":
    get_max_id(config.TEXT_CLIP_INDEX)