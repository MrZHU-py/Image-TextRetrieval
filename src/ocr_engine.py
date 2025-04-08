'''
FilePath: \TextRetrieval\src\ocr_engine.py
Author: ZPY
TODO: 
'''
import pytesseract
import easyocr
import cv2
import config

# 设置 Tesseract 位置
pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD
reader = easyocr.Reader(['en', 'ch_sim'])  # 使用 EasyOCR 进行 OCR 识别

def extract_text_tesseract(image):
    """使用 Tesseract 进行 OCR 识别"""
    return pytesseract.image_to_string(image, lang='chi_sim')

def extract_text_easyocr(image):
    """使用 EasyOCR 进行 OCR 识别"""
    results = reader.readtext(image)
    return " ".join([res[1] for res in results])
