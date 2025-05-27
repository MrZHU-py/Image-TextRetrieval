'''
FilePath: \\Image-TextRetrieval\\tools\\del_data.py
Author: ZPY
TODO: 
'''
import sys
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError

def delete_document(index_name, doc_id):
    # 连接到 Elasticsearch（默认 localhost:9200）
    es = Elasticsearch(hosts=["http://localhost:9200"])

    try:
        # 检查文档是否存在
        if es.exists(index=index_name, id=doc_id):
            # 删除文档
            es.delete(index=index_name, id=doc_id)
            print(f"Document with _id '{doc_id}' deleted from index '{index_name}'.")
        else:
            print(f"Document with _id '{doc_id}' does not exist in index '{index_name}'.")
    except NotFoundError:
        print(f"Index '{index_name}' or document '{doc_id}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python del_data.py <index_name> <doc_id>")
        sys.exit(1)

    index = sys.argv[1]
    doc_id = sys.argv[2]

    delete_document(index, doc_id)
