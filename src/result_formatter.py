'''
FilePath: \Image-TextRetrieval\src\result_formatter.py
Author: ZPY
TODO: 检索结果格式化模块
'''

def format_search_results(search_results):
    """格式化文本检索结果"""
    if not search_results:
        return "No matching results found."
    
    formatted_text = ""
    for idx, hit in enumerate(search_results, 1):
        content = hit['_source'].get('content', 'No content available')
        formatted_text += f"Result {idx}:\n"
        formatted_text += f"{content}\n"
        formatted_text += "-" * 40 + "\n"
    
    return formatted_text

def format_image_search_results(search_results):
    """格式化图像检索结果"""
    if not search_results:
        return "No similar images found."
    
    formatted_text = ""
    for idx, hit in enumerate(search_results, 1):
        image_path = hit['_source'].get('image_path', 'No image path available')
        score = hit.get('_score', 0.0)
        formatted_text += f"Result {idx}:\n"
        formatted_text += f"Image Path: {image_path}\n"
        formatted_text += f"Score: {score:.2f}\n"
        formatted_text += "-" * 40 + "\n"
    
    return formatted_text