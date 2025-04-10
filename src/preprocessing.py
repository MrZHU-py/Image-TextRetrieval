'''
FilePath: \\Image-TextRetrieval\\src\\preprocessing.py
Author: ZPY
TODO: 图像预处理模块
'''
import cv2
import numpy as np

def is_screenshot(image):
    """
    判断图像是否为截图
    :param image: 输入图像
    :return: True 表示截图，False 表示照片
    """
    # 转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 计算图像的拉普拉斯方差（用于检测模糊程度）
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

    # 计算图像的对比度
    contrast = gray.max() - gray.min()

    # 如果拉普拉斯方差较高且对比度较高，认为是截图
    if laplacian_var > 500 and contrast > 100:
        return True
    return False

def preprocess_image(image_path_or_array):
    """
    加载并预处理图片
    :param image_path_or_array: 图片路径或图像数组
    :return: 预处理后的图像
    """
    # 如果输入是路径，加载图像
    if isinstance(image_path_or_array, str):
        image = cv2.imread(image_path_or_array, cv2.IMREAD_COLOR)
    else:
        image = image_path_or_array

    # 判断是否为截图
    if is_screenshot(image):
        print("Detected as screenshot.")
        # 针对截图的预处理
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
        return binary
    else:
        print("Detected as photo.")
        # 针对照片的预处理
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # 应用自适应直方图均衡化（CLAHE）以增强对比度
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        # 使用高斯模糊去除噪声
        denoised = cv2.GaussianBlur(enhanced, (5, 5), 0)
        # 使用 Otsu 自动阈值进行二值化处理
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # 校正图像中的倾斜文本
        corrected = correct_skew(binary, angle_threshold=2)
        # 使用形态学闭运算去除噪声并连接断裂的文本行
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
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    if abs(angle) < angle_threshold:
        return image
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

def preprocess_and_recognize(image_path):
    """预处理图像并进行 OCR 识别"""
    # 预处理图像
    preprocessed_image = preprocess_image(image_path)
    
    # OCR 识别
    extracted_text = extract_text_tesseract(preprocessed_image)
    return extracted_text
