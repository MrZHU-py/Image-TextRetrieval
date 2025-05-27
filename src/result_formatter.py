'''
FilePath: \\Image-TextRetrieval\\src\\result_formatter.py
Author: ZPY
TODO: 检索结果格式化模块
'''

def format_search_results(search_results):
    """格式化文本检索结果为HTML，链接本身为超链接文本"""
    if not search_results:
        return "暂无匹配结果。"
    
    formatted_text = ""
    for idx, hit in enumerate(search_results, 1):
        content = hit['_source'].get('content', '暂无内容')
        url = hit['_source'].get('url', '')
        formatted_text += f"<b>结果 {idx}:</b><br>"
        formatted_text += f"{content}<br>"
        if url:
            formatted_text += f'<b>相关文档链接：<a href="{url}">{url}</a></b><br>'
        formatted_text += "<hr>"
    return formatted_text
