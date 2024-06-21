import re
import cv2
import base64
import numpy as np

def is_base_str(input_str):
    """Modeify data format.

    Args:
        input_str: a base64 format string.
    """
    pattern = "^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{4}|[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)$"
    return re.match(pattern, input_str)


def image_to_base64(img_np):
    image = cv2.imencode('.jpg', img_np)[1]
    image_code = str(base64.b64encode(image), encoding='utf-8')
    return image_code


def base64_to_image(base64_code):
    image_data = base64.b64decode(base64_code)
    # transform to np
    image_np = np.fromstring(image_data, np.uint8)
    # opencv format
    image = cv2.imdecode(image_np, cv2.COLOR_RGB2BGR)
    return image