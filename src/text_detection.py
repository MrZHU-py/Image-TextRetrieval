'''
FilePath: \\Image-TextRetrieval\\src\\text_detection.py
Author: ZPY
TODO: 
'''
import cv2
import numpy as np

def is_screenshot(image):
    """判断图像是否为截图"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    contrast = gray.max() - gray.min()
    return laplacian_var > 500 and contrast > 100

def filter_regions(regions, min_area=100, max_area=10000, min_aspect_ratio=0.2, max_aspect_ratio=5.0):
    """过滤检测到的文本区域"""
    filtered_regions = []
    for p in regions:
        x, y, w, h = cv2.boundingRect(p.reshape(-1, 1, 2))
        area = w * h
        aspect_ratio = w / h if h > 0 else 0
        if min_area <= area <= max_area and min_aspect_ratio <= aspect_ratio <= max_aspect_ratio:
            filtered_regions.append((x, y, w, h))
    return filtered_regions

def detect_text_regions(image):
    """使用 MSER 进行文本区域检测"""
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    mser = cv2.MSER_create()
    regions, _ = mser.detectRegions(image)

    filtered_regions = filter_regions(regions)

    output = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    for idx, (x, y, w, h) in enumerate(filtered_regions):
        cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(output, f"{idx + 1}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    return output, filtered_regions
