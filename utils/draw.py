import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

def AddText(cv_img, text, left, top, textColor=(255, 0, 0), textSize=30):
    # cv -> pil
    if (isinstance(cv_img, np.ndarray)):
        img = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    fontStyle = ImageFont.truetype("simsun.ttc", textSize, encoding='utf-8')
    draw.text((left, top), text, textColor, font=fontStyle)
    # convert to cv style
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)


def opencvAddText(cv_img, text, left, top, textColor=(0, 0, 255)):
    font = cv2.FONT_HERSHEY_SIMPLEX
    return cv2.putText(cv_img, text, (left, top), font, 1, textColor, 2)


def draw_pr_curve(recall, precision, figure_file):
    plt.plot(recall, precision, lw = 2)
    fontsize = 14
    plt.xlabel('Recall', fontsize = fontsize)
    plt.ylabel('Precision', fontsize = fontsize)
    plt.title('Precision Recall Curve')
    # plt.legend()
    plt.savefig(figure_file)
    plt.close()

def draw_bar(box_dis, figure_file):
    xlabel = list(box_dis.keys())
    ylabel = list(box_dis.values())
    plt.bar(xlabel, ylabel)
    for a,b in zip(xlabel, ylabel):
        plt.text(a,b,'%.2f'%b,ha='center',va='bottom',fontsize=7)
    plt.title("Box Size Distribution")
    plt.savefig(figure_file)

def draw_polygen(image, boxes, color=(255, 0, 0)):
    if not isinstance(boxes,(np.ndarray, list)):
        raise TypeError(str(type(boxes)) + "is not np.ndarray or list")
    if isinstance(boxes, np.ndarray):
        boxes = boxes.astype(int)
        image = cv2.polylines(image, boxes, True, color, 3)
    else:
        for box in boxes:
            cv2.rectangle(image, (box[0], box[1]), (box[2], box[3]), color, thickness=2)
    return image