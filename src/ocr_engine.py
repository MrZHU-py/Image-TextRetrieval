'''
FilePath: \\Image-TextRetrieval\\src\\ocr_engine.py
Author: ZPY
TODO: OCR 引擎模块：提供文字识别功能
'''
import cv2
import logging
import numpy as np
import easyocr
import pytesseract
from paddleocr import PaddleOCR
import config  # 引入全局配置

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levellevel)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OCREngine:
    """OCR 引擎：PaddleOCR -> EasyOCR -> Tesseract"""

    def __init__(self,
                 paddle_lang='ch',
                 use_angle_cls=True,
                 det=True, rec=True, cls=True,
                 easyocr_langs=None,
                 easyocr_gpu=False,
                 tesseract_lang='chi_sim+eng',
                 tesseract_psm=6,
                 tesseract_oem=3):
        # PaddleOCR 初始化
        try:
            self.paddle = PaddleOCR(
                lang=paddle_lang,
                use_angle_cls=use_angle_cls,
                det=det, rec=rec, cls=cls,
                enable_mkldnn=True
            )
            logger.info("PaddleOCR 初始化成功")
        except Exception as e:
            logger.error(f"PaddleOCR 初始化失败: {e}")
            self.paddle = None

        # EasyOCR 初始化
        if easyocr_langs is None:
            easyocr_langs = ['ch_sim', 'en']
        try:
            self.easyocr = easyocr.Reader(easyocr_langs, gpu=easyocr_gpu)
            logger.info("EasyOCR 初始化成功")
        except Exception as e:
            logger.error(f"EasyOCR 初始化失败: {e}")
            self.easyocr = None

        # Tesseract 参数
        self.tess_lang = tesseract_lang
        self.tess_cfg = f'--oem {tesseract_oem} --psm {tesseract_psm}'

    def extract_text(self, image: np.ndarray) -> str:
        """
        纯文本识别：
        1. PaddleOCR
        2. EasyOCR（Fallback）
        3. Tesseract（最终回退）
        """
        text = ""
        # 1) PaddleOCR
        if self.paddle:
            try:
                res = self.paddle.ocr(image, cls=True)
                lines = [line[1][0] for block in res for line in block if line[1][0].strip()]
                text = "\n".join(lines).strip()
            except Exception as e:
                logger.warning(f"PaddleOCR 识别失败: {e}")

        # 2) EasyOCR
        if not text and self.easyocr:
            try:
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                easy_res = self.easyocr.readtext(rgb, detail=0, paragraph=False)
                text = "\n".join([t for t in easy_res if t.strip()]).strip()
            except Exception as e:
                logger.warning(f"EasyOCR 识别失败: {e}")

        # 3) Tesseract
        if not text:
            try:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                text = pytesseract.image_to_string(gray,
                                                   lang=self.tess_lang,
                                                   config=self.tess_cfg).strip()
            except Exception as e:
                logger.error(f"Tesseract 识别失败: {e}")
                text = ""
        return text

# 全局 OCR 引擎实例
ocr_engine = OCREngine(
    paddle_lang='ch',
    use_angle_cls=True,
    det=True, rec=True, cls=True,
    easyocr_langs=['ch_sim', 'en'],
    easyocr_gpu=False,
    tesseract_lang='chi_sim+eng',
    tesseract_psm=6,
    tesseract_oem=3
)

def extract_text_ocr(image: np.ndarray) -> str:
    return ocr_engine.extract_text(image)


