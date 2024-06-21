import os
import sys
import cv2
import uuid
import torch
import numpy as np

from add_noise import add_noise
from files import get_file_list, read_file
from boxes_process import compute_iou

TEMPLATE_CLASS1 = ["columnar-most", "columnar-more", "rect-pos", "square",
                   "rect-neg", "stick-more", "stick-most"]
TEMPLATE_CLASS2 = ["20", "30", "40", "50", "60", 
                   "90", "120", "180", "240", "300"]

def collect_templates(templates_dir, ratio_thr, noise_type, debug_dir):
    """
    """
    template_images = {}
    for key1 in TEMPLATE_CLASS1:
        template_images[key1] = {}
        for key2 in TEMPLATE_CLASS2:
            template_images[key1][key2] = []
    # template dataset
    if not os.path.exists(templates_dir):
        print("{} not exists, please check".format(templates_dir))
        return template_images
    
    template_lists = get_file_list(templates_dir, type='image')
    for template_file in template_lists:
        # template info
        template_image = cv2.imread(os.path.join(templates_dir, template_file))
        template_h, template_w, template_c = template_image.shape

        template_label_file = os.path.join(templates_dir, os.path.splitext(template_file)[0] + '.txt')
        template_labels = read_file(os.path.join(templates_dir, template_label_file))

        
        for label in template_labels:
            label_arr = [float(v) for v in label.strip().split(' ')]
            box_w = int(label_arr[3] * template_w)
            box_h = int(label_arr[4] * template_h)
            box_cx = int(label_arr[1] * template_w)
            box_cy = int(label_arr[2] * template_h)

            template_patch = template_image[int(box_cy - box_h/2):int(box_cy + box_h/2),
                                                    int(box_cx - box_w/2):int(box_cx + box_w/2),
                                                    :]
            ratio = box_w / box_h
            if ratio < ratio_thr or ratio > 1 / ratio_thr:
                continue
            average_size = int((box_w + box_h)/2)
            ratio_type, size_type = classify_template(ratio, average_size)
            if ratio_type == None or size_type == None:
                continue
            # add noise to template
            if np.random.rand() > 0.5:
                template_patch = add_noise(template_patch, noise_type)

            template_images[ratio_type][size_type].append(template_patch)
            # save template images for debug
            if os.path.isdir(debug_dir):
                cv2.imwrite(os.path.join(debug_dir, str(uuid.uuid1()) + '.png'), template_patch)
    return template_images

def random_choose_templates(templates, max_num=5):
    """
    """
    current_templates = []
    while True:
        choose_ratio_type = TEMPLATE_CLASS1[np.random.randint(len(TEMPLATE_CLASS1))]
        choose_size_type = TEMPLATE_CLASS2[np.random.randint(len(TEMPLATE_CLASS2))]
        if len(templates[choose_ratio_type][choose_size_type]) >= 1:
            index = np.random.randint(len(templates[choose_ratio_type][choose_size_type]))
            current_templates.append(templates[choose_ratio_type][choose_size_type][index])
        if len(current_templates) == max_num:
            break    
    return current_templates

def classify_template(ratio, size):
    ratio_type, size_type = None, None
    if ratio <= 0.25:
        pass
    elif ratio > 0.25 and ratio <= 0.3:
        ratio_type = "columnar-most"
    elif ratio > 0.3 and ratio <= 0.5:
        ratio_type = "columnar-more"
    elif ratio > 0.5 and ratio <= 0.8:
        ratio_type = "rect-pos"
    elif ratio > 0.8 and ratio <= 1.2:
        ratio_type = "square"
    elif ratio > 1.2 and ratio <= 2:
        ratio_type = "rect-neg"
    elif ratio > 2 and ratio <= 3:
        ratio_type = "stick-more"
    elif ratio > 3 and ratio <= 4:
        ratio_type = "stick-most"
    else:
        pass

    if size <= 20:
        size_type = "20"
    elif size > 20 and size <= 30:
        size_type = "30"
    elif size > 30 and size <= 40:
        size_type = "40"
    elif size > 40 and size <= 50:
        size_type = "50"
    elif size > 50 and size <= 60:
        size_type = "60"
    elif size > 60 and size <= 90:
        size_type = "90"
    elif size > 90 and size <= 120:
        size_type = "120"
    elif size > 120 and size <= 180:
        size_type = "180"
    elif size > 180 and size <= 240:
        size_type = "240"
    elif size > 240 and size <= 300:
        size_type = "300"
    else:
        pass
    return ratio_type, size_type

def replace_paste(src_image, src_labels, templates, 
                  ratio_res_thr=0.5, ratio_thr=0.3, 
                  pad=False, pad_max_pixel=6, pad_ratio=0.1):
    """
    """
    src_h, src_w, _ = src_image.shape
    labels = []
    for label in src_labels:
        label_arr = [float(v) for v in label.strip().split(' ')]
        box_w = int(label_arr[3] * src_w)
        box_h = int(label_arr[4] * src_h)
        box_cx = int(label_arr[1] * src_w)
        box_cy = int(label_arr[2] * src_h)
        box = [int(box_cx - box_w/2), int(box_cy - box_h/2), 
               int(box_cx + box_w/2), int(box_cy + box_h/2)]
        ratio = box_w / box_h
        if ratio < ratio_thr or ratio > 1 / ratio_thr:
            continue
        average_size = int((box_w + box_h)/2)

        # choose template according to size and ratio
        ratio_type, size_type = classify_template(ratio, average_size)
        if ratio_type == None or size_type == None:
            continue
        if len(templates[ratio_type][size_type]) == 0:
            continue

        min_res = sys.float_info.max
        min_index = -1
        for index, template in enumerate(templates[ratio_type][size_type]):
            template_h, template_w, _ = template.shape
            template_ratio = template_w / template_h
            if np.abs(ratio - template_ratio) > ratio_res_thr:
                continue
            if np.abs(ratio - template_ratio) < min_res:
                min_index = index
        if min_index != -1:
            resize_temp = cv2.resize(templates[ratio_type][size_type][min_index], (box[2]-box[0], box[3]-box[1]))
            src_image[box[1]:box[3], box[0]:box[2], :] = resize_temp
            labels.append(label)
    return src_image, labels

def random_paste(src_image, templates, iou_thr):
    """
    """
    src_h, src_w, _ = src_image.shape
    current_templates = random_choose_templates(templates, np.random.randint(1, 10))
    labels = []
    boxes = []

    for template_image in current_templates:
        template_h, template_w, _ = template_image.shape
        x1 = max(int(np.floor((src_w - template_w) * np.random.rand())), 0)
        y1 = max(int(np.floor((src_h - template_h) * np.random.rand())), 0)
        if (x1 + template_w) >= src_w or (y1 + template_h) >= src_h:
            print("random paste location out of image")
            continue
        box = [x1, y1, x1+template_w, y1+template_h]
        if len(boxes)>0:
            ious = compute_iou(torch.from_numpy(np.array([box])), 
                                         torch.from_numpy(np.array(boxes)))
            max_iou = np.max(ious.numpy())
            if max_iou > iou_thr:
                continue
        # paste
        src_image[y1:y1+template_h, x1:x1+template_w, :] = template_image
        label_str = '{} {} {} {} {}\n'.format(0,
                                              (x1+template_w/2)/src_w,
                                              (y1+template_h/2)/src_h,
                                              template_w/src_w,
                                              template_h/src_h)
        labels.append(label_str)
        boxes.append(box)
    return src_image, labels

def iou_paste(src_image, src_labels, templates, iou_thr):
    """
    """
    src_h, src_w, _ = src_image.shape
    labels = []
    boxes = []
    current_templates = random_choose_templates(templates, len(src_labels))
    if len(current_templates) == 0:
        return src_image, labels
    
    for label in src_labels:
        label = [float(v) for v in label.strip().split(" ")]
        box_w = int(label[3] * src_w)
        box_h = int(label[4] * src_h)
        box_x1 = int(label[1] * src_w - box_w / 2)
        box_y1 = int(label[2] * src_h - box_h / 2)
        
        template_image = current_templates[np.random.randint(len(current_templates))]
        template_h, template_w, _ = template_image.shape

        patch_x1, patch_y1 = -1, -1
        if max(box_x1 - template_w - 1, 0) <  min(box_x1 + template_w, src_w - template_w -1):
            patch_x1 = np.random.randint(max(box_x1 - template_w - 1, 0),
                                        min(box_x1 + template_w, src_w - template_w -1))
        if max(box_y1 - template_h - 1, 0) < min(box_y1 + template_h, src_h - template_h -1):
            patch_y1 = np.random.randint(max(box_y1 - template_h - 1, 0),
                                        min(box_y1 + template_h, src_h - template_h -1))
        if patch_x1 == -1 or patch_y1 == -1:
            print("patch x & y init failed")
            continue
        if (patch_x1 + template_w) >= src_w or (patch_y1 + template_h) >= src_h:
            print("iou paste location out of image")
            continue
        box = [patch_x1, patch_y1, patch_x1+template_w, patch_y1+template_h]

        if len(boxes) > 0:
            ious = compute_iou(torch.from_numpy(np.array([box])), 
                                         torch.from_numpy(np.array(boxes)))
            max_iou = np.max(ious.numpy())
            if max_iou > iou_thr:
                continue

        src_image[patch_y1:patch_y1+template_h, patch_x1:patch_x1+template_w, :] = template_image
        label_str = '{} {} {} {} {}\n'.format(0,
                                              (patch_x1 + template_w/2)/src_w,
                                              (patch_y1 + template_h/2)/src_h,
                                              template_w/src_w,
                                              template_h/src_h)
        labels.append(label_str)
        boxes.append(box)
    return src_image, labels
