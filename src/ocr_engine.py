'''
FilePath: \\Image-TextRetrieval\\src\\ocr_engine.py
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
    """使用 PaddleOCR 提取文本"""
    try:
        # 使用 open 和 cv2.imdecode 加载图片，解决中文路径问题
        with open(image_path, 'rb') as f:
            file_bytes = np.asarray(bytearray(f.read()), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError(f"无法加载图像，请检查路径或文件格式：{image_path}")

        # 使用 PaddleOCR 进行文本提取
        ocr = PaddleOCR(use_angle_cls=True, lang='ch')  # 支持中文
        result = ocr.ocr(image, cls=True)

        # 提取文本
        extracted_text = "\n".join([line[1][0] for line in result[0]])
        return extracted_text
    except Exception as e:
        print(f"Error in extract_text_paddleocr: {e}")
        return ""