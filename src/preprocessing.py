'''
FilePath: \TextRetrieval\src\preprocessing.py
Author: ZPY
TODO: 
'''
import cv2
import numpy as np

def preprocess_image(image_path):
    """
    加载并预处理图片
    :param image_path: 图片路径
    :return: 预处理后的图像
    """
    # 加载图像
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    
    # 转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 自适应直方图均衡化（CLAHE）增强对比度
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # 去噪（高斯模糊）
    denoised = cv2.GaussianBlur(enhanced, (5, 5), 0)
    
    # 二值化（Otsu 阈值）
    _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # 倾斜校正（自动判断是否需要校正）
    corrected = correct_skew(binary, angle_threshold=2)
    
    # 形态学操作（闭运算修复断裂的字符）
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    morphed = cv2.morphologyEx(corrected, cv2.MORPH_CLOSE, kernel)
    
    return morphed

def correct_skew(image, angle_threshold=2):
    """
    校正图像中的倾斜文本
    :param image: 输入的二值化图像
    :param angle_threshold: 倾斜角度阈值，超过该值才进行校正
    :return: 校正后的图像
    """
    # 找到非零像素的坐标
    coords = np.column_stack(np.where(image > 0))
    # 计算最小外接矩形的角度
    angle = cv2.minAreaRect(coords)[-1]
    # 调整角度范围
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    # 判断是否需要校正
    if abs(angle) < angle_threshold:
        return image
    # 获取图像中心
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    # 生成旋转矩阵
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    # 旋转图像
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated
