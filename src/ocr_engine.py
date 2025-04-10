'''
FilePath: \Image-TextRetrieval\src\ocr_engine.py
Author: ZPY
TODO: 整合 PaddleOCR 和预处理模块
'''
import pytesseract
import easyocr
import cv2
from PIL import Image  # 导入 Pillow
import numpy as np
import config
from paddleocr import PaddleOCR
from src.preprocessing import preprocess_image

# 设置 Tesseract 位置
pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD
reader = easyocr.Reader(['en', 'ch_sim'])  # 使用 EasyOCR 进行 OCR 识别

def extract_text_tesseract(image):
    """使用 Tesseract 进行 OCR 识别"""
    # 将 OpenCV 图像 (NumPy 数组) 转换为 Pillow 图像
    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)
    return pytesseract.image_to_string(image, lang='chi_sim')

def extract_text_easyocr(image):
    """使用 EasyOCR 进行 OCR 识别"""
    results = reader.readtext(image)
    return " ".join([res[1] for res in results])

def extract_text_paddleocr(image_path):
    """使用 PaddleOCR 进行文本识别"""
    # 加载图像为 NumPy 数组
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Failed to load image: {image_path}")

    # 使用 PaddleOCR 进行识别
    ocr = PaddleOCR(use_angle_cls=True, lang='ch')  # 支持中文
    result = ocr.ocr(image, cls=True)
    extracted_text = "\n".join([line[1][0] for line in result[0]])
    return extracted_text