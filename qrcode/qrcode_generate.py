
import cv2
import qrcode
import numpy as np
from PIL import Image

from utils.files import is_file


def qrcode_generate(qrcode_info, **kwargs):
    assert qrcode_info != '', "QR code info is null."
    version = kwargs['version'] if 'version' in kwargs else None
    box_size = kwargs['box_size'] if 'box_size' in kwargs else 10
    border = kwargs['border'] if 'border' in kwargs else 4 
    qr = qrcode.QRCode(
        version=version,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border
    )
    qr.add_data(qrcode_info)
    qr.make()
    qrcode_image = qr.make_image()
    return qrcode_image


def qrcode_generate_and_save(qrcode_info, save_path, **kwargs):
    qrcode_image = qrcode_generate(qrcode_info, **kwargs)
    if save_path and is_file(save_path, type='image'):
        qrcode_image.save(save_path)


def qrcode_with_image(image, qrcode_info, save_path, **kwargs):
    assert image is not None, "Input image is null."
    if isinstance(image, np.ndarray):
        image = Image.fromarray(cv2.cvtColor(image,cv2.COLOR_BGR2RGB))

    # fill_color = kwargs['fill_color'] if 'fill_color' in kwargs else None #'red'
    # back_color = kwargs['back_color'] if 'back_color' in kwargs else None #'#23dda0'
    qrcode_image = qrcode_generate(qrcode_info, **kwargs) #(fill_color=fill_color, back_color=back_color)

    img_post = kwargs['img_post'] if 'img_post' in kwargs else (image.size[0]//2, image.size[1]//2)
    qrcode_size = kwargs['qrcode_size'] if 'qrcode_size' in kwargs else (qrcode_image.size[0], qrcode_image.size[0])
    if save_path and is_file(save_path, type='image'):
        if qrcode_size[0] != qrcode_image.size[0] or qrcode_size[1] != qrcode_image.size[1]:
            qrcode_image = qrcode_image.resize(qrcode_size, Image.BICUBIC)
        image.paste(qrcode_image, img_post)
        image.save(save_path)




    
