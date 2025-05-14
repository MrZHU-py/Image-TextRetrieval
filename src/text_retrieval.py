'''
FilePath: \Image-TextRetrieval\src\text_retrieval.py
Author: ZPY
TODO: 连接 Elasticsearch，提供索引和搜索功能
'''
import config
import numpy as np
from config import es_client as es  # 使用配置文件中的 ES 实例
import config
import numpy as np
from config import es_client as es  # 使用配置文件中的 ES 实例

def search_text(query, top_k=10):
    """在 Elasticsearch 中进行文本检索"""
    try:
        if not isinstance(query, str):
            raise ValueError("Query must be a string.")

        # 生成查询嵌入
        from config import m3e_model
        query_embedding = m3e_model.encode(query)
        normalized_query_embedding = (query_embedding / np.linalg.norm(query_embedding)).tolist()

        script_query = {
            "size": top_k,
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                        "params": {"query_vector": normalized_query_embedding}
                    }
                }
            }
        }

        try:
            response = es.search(
                index=config.TEXT_INDEX,
                body=script_query
            )
            return response['hits']['hits']
        except Exception as e:
            print(f"Elasticsearch search error: {str(e)}")
            return []

    except Exception as e:
        print(f"Error in search_text: {e}")
        return []