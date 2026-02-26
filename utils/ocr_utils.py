import os
import numpy as np
import streamlit as st
from paddleocr import PaddleOCR
from utils.image_utils import resize_for_ocr

# Prevent PaddleOCR pipeline issues
os.environ["DISABLE_MODEL_SOURCE_CHECK"] = "True"


# ✅ PaddleOCR MUST be cached (Streamlit-safe)
@st.cache_resource(show_spinner=False)
def get_ocr():
    return PaddleOCR(
        lang="en",
        use_angle_cls=False,
        use_gpu=False,
        show_log=False
    )


def extract_ocr_from_image(image):
    ocr = get_ocr()  # ✅ Safe, single instance

    img = resize_for_ocr(image)
    img_np = np.array(img)

    try:
        result = ocr.ocr(img_np, cls=False)
    except Exception as e:
        print("OCR failed:", e)
        return [], []

    words, boxes = [], []

    if not result:
        return words, boxes

    h, w = img_np.shape[:2]

    for line in result:
        for item in line:
            box, (text, _) = item
            text = text.strip()

            if not text:
                continue

            x0, y0 = box[0]
            x2, y2 = box[2]

            boxes.append([
                int(1000 * x0 / w),
                int(1000 * y0 / h),
                int(1000 * x2 / w),
                int(1000 * y2 / h),
            ])
            words.append(text)

    return words, boxes
