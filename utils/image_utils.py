from PIL import Image

MAX_SIDE = 1600  # safe for OCR, avoids kernel crash


def resize_for_ocr(image: Image.Image) -> Image.Image:
    """
    Resize image so that the longest side <= MAX_SIDE
    while keeping aspect ratio.
    """
    w, h = image.size
    scale = min(MAX_SIDE / max(w, h), 1.0)

    if scale < 1.0:
        image = image.resize(
            (int(w * scale), int(h * scale)),
            Image.BILINEAR
        )

    return image
