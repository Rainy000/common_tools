import cv2
import numpy as np
from pyzbar.pyzbar import decode

def qrcode_detect_opencv(image, mode):
    qcd = cv2.QRCodeDetector()
    if mode == 'one':
        codeinfo, points, _ = qcd.detectAndDecode(image)
    elif mode == 'multi':
        ret_qr, codeinfo, points, _ = qcd.detectAndDecodeMulti(image)
    return codeinfo, points


def qrcode_detect_pyzbar(image):
    boxes = []
    codeinfo = []

    for d in decode(image):
        boxes.append(np.array(d.polygon))
        codeinfo.append(d.data.decode())
    return tuple(codeinfo), np.array(boxes)


def qrcode_detect_qrdet(detector, image):
    detections = detector.detect(image=image, is_bgr=False)
    boxes = []
    scores = []
    for detection in detections:
        x1, y1, x2, y2 = detection['bbox_xyxy']
        boxes.append([int(x1), int(y1), int(x2), int(y2)])
        confidence = detection['confidence']
        scores.append(confidence)
    return scores, boxes
