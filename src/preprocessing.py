'''
FilePath: \Image-TextRetrieval\src\preprocessing.py
Author: ZPY
TODO: 图像预处理模块
'''
import cv2
import numpy as np


def is_screenshot(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    median = np.median(gray)
    noise_pixels = np.sum(np.abs(gray.astype(np.float32) - median) > 25)
    return noise_pixels / gray.size < 0.015

def preprocess_image(image_path_or_array, enhance=True, deskew=True, upscale=True):
    """
    加载并预处理图片，返回原图和适合 Tesseract 的三通道 BGR 图像
    """
    # 加载原图
    if isinstance(image_path_or_array, str):
        data = np.fromfile(image_path_or_array, dtype=np.uint8)
        image = cv2.imdecode(data, cv2.IMREAD_COLOR)
    else:
        image = image_path_or_array

    if image is None:
        raise ValueError(f"无法加载图像：{image_path_or_array}")
    orig = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 放大低分辨率
    if upscale and min(gray.shape) < 40:
        scale = 2 if min(gray.shape) < 20 else 1.5
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    # 轻度增强
    if enhance:
        clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
        gray = clahe.apply(gray)

    # 二值化（仅截图或对比度低）
    if is_screenshot(image) or np.std(gray) < 30:
        proc = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 25, 15
        )
    else:
        proc = gray

    # 倾斜校正
    if deskew:
        proc = correct_skew(proc)

    # 转三通道 BGR，以便所有后续模块直接按照三通道处理
    proc_bgr = cv2.cvtColor(proc, cv2.COLOR_GRAY2BGR)
    return orig, proc_bgr

def correct_skew(image, angle_threshold=2):
    """
    校正图像中的倾斜文本
    :param image: 输入的二值化图像
    :param angle_threshold: 倾斜角度阈值，超过该值才进行校正
    :return: 校正后的图像
    """
    coords = np.column_stack(np.where(image > 0))
    if coords.shape[0] == 0:
        return image
    angle = cv2.minAreaRect(coords)[-1]
    # 修正角度范围
    if angle < -45:
        angle = 90 + angle
    # 只对小角度倾斜做校正，避免大角度翻转
    if abs(angle) < angle_threshold or abs(angle) > 30:
        return image
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated
