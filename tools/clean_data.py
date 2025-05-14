# clean_data_bulk_timeout.py — Windows/Linux 通用，防止 Bulk 超时

import re
from elasticsearch import Elasticsearch, helpers

# 索引名
INDEX_NAME = "text_clip_index"
# 匹配末尾两个及以上中文句号
TRAILING_DOTS_RE = re.compile(r"(.*?)。{2,}$")

def scan_and_prepare_actions(es: Elasticsearch, index: str):
    """
    滚动扫描所有文档，收集需要更新的 bulk action 列表。
    """
    actions = []
    for doc in helpers.scan(
        es, index=index,
        query={"_source": ["text"], "query": {"match_all": {}}},
        scroll="5m"  # 长滚动上下文，防止大索引扫描中断
    ):
        doc_id = doc["_id"]
        text = doc["_source"].get("text", "")
        m = TRAILING_DOTS_RE.match(text)
        if m:
            new_text = m.group(1) + "。"
            actions.append({
                "_op_type": "update",
                "_index": index,
                "_id": doc_id,
                "doc": {"text": new_text}
            })
    return actions

def main():
    es = Elasticsearch(
        hosts=["http://localhost:9200"],
        timeout=60  # ES 客户端整体超时设置
    )
    print(f"扫描索引 `{INDEX_NAME}` 中的所有文档…")
    actions = scan_and_prepare_actions(es, INDEX_NAME)
    total = len(actions)
    print(f"共找到 {total} 条需要更新。")

    if total == 0:
        print("无需更新，退出。")
        return

    print("开始批量更新…")
    # bulk 更新
    success, failed = helpers.bulk(
        es,
        actions,
        chunk_size=1000,         # 每批 1000 条，减轻单次负载
        refresh=True,            # 每批都刷新，使进度可见
        request_timeout=60       # 单次请求超时 60s
    )
    print(f"批量更新完成：成功 {success} 条，失败 {failed} 条。")

if __name__ == "__main__":
    main()
