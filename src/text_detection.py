'''
FilePath: \TextRetrieval\src\text_detection.py
Author: ZPY
TODO: 
'''
import cv2
import numpy as np

def detect_text_regions(image):
    """使用 MSER 进行文本区域检测"""
    mser = cv2.MSER_create()
    regions, _ = mser.detectRegions(image)
    
    # 画出检测到的文本区域
    output = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    for p in regions:
        x, y, w, h = cv2.boundingRect(p.reshape(-1, 1, 2))
        cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    return output
