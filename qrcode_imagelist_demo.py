import os
import cv2
import time
import argparse
import numpy as np
from tqdm import tqdm
from qrdet import QRDetector
import matplotlib.pyplot as plt

from utils.files import get_file_list
from utils.boxes_process import poly_to_box 
from utils.draw import draw_polygen, draw_bar, draw_pr_curve
from utils.voc_eval import voc_eval
from utils.distribution_analysis import annotations_distribution, \
                                        detection_distribution
from qrcode.qrcode_detect import qrcode_detect_opencv, \
                                 qrcode_detect_pyzbar, qrcode_detect_qrdet

def args_parse():
    parser = argparse.ArgumentParser(description='QR code detect.')
    parser.add_argument('root', type=str, help='Root path for operation.')
    parser.add_argument('subdir', type=str, help='Image sub directory name.')
    parser.add_argument('imglist_file', type=str, help='File name to save image name list.')
    parser.add_argument(
        '--class-name',
        type=str, 
        default='QR_CODE', 
        help='Name of object class.'
    )
    parser.add_argument(
        '--algo',
        type=str,
        default='opencv',
        choices=['opencv', 'pyzbar', 'qrdet'],
        help='Algorithms for qr code detect.'
    )
    parser.add_argument(
        '--save', 
        action='store_true', 
        help='Save detect and annotation result image.'
    )
    parser.add_argument(
        '--mode',
        default='multi',
        choices=['one', 'multi'],
        help='Detect one or multi qr code, only used in opencv algorithm'
    )
    parser.add_argument(
        '--show',
        action='store_true', 
        help='Display the image in a popup window or not.'
    )
    parser.add_argument(
        '--size',
        type=int,
        nargs='+',
        default=[40, 64, 96],
        help='Using group the annotation/detection box size distribution.'
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = args_parse()
    print(args)

    # get image name list
    image_full_path = os.path.join(args.root, args.subdir)
    imagelists = [os.path.splitext(image_name)[0] 
                  for image_name in get_file_list(image_full_path, type='image')]
    

    # save image name list to file
    image_header = open(os.path.join(args.root, args.imglist_file), 'w')
    for image_name in imagelists:
        image_header.write('{}\n'.format(image_name))
    image_header.close()

    # init qrdet algo if need
    detector = None
    if args.algo == 'qrdet':
        detector = QRDetector(model_size='n', conf_th=0.01)

    # traverse all image and get detection results
    det_file = '{}_det.txt'.format(args.algo)
    full_det_file = args.class_name + '_' + det_file
    det_header = open(os.path.join(args.root, full_det_file), 'w')

    image_bar = tqdm(imagelists)
    total_time = 0
    for image_path in image_bar:
        full_path = os.path.join(image_full_path, image_path+'.jpg')
        bgr_image = cv2.imread(full_path)
        gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
        
        if args.algo == 'opencv':
            s_time = time.time()
            codeinfo, polygens = qrcode_detect_opencv(gray_image, args.mode)
            total_time += (time.time() - s_time)
        elif args.algo == 'pyzbar':
            s_time = time.time()
            codeinfo, polygens = qrcode_detect_pyzbar(gray_image)
            total_time += (time.time() - s_time)
        elif args.algo == 'qrdet' and detector is not None:
            s_time = time.time()
            scores, polygens = qrcode_detect_qrdet(detector, gray_image)
            total_time += (time.time() - s_time)
        
        # format convert and save
        if polygens is None or len(polygens)==0:
            # print("polygens is empty")
            if args.save:
                save_full_path = os.path.join(args.root, args.algo, 'no_det')
                if not os.path.exists(save_full_path):
                    os.makedirs(save_full_path)
                cv2.imwrite(os.path.join(save_full_path, image_path+'.jpg'), bgr_image)
        else:
            if args.algo != 'qrdet':
                boxes = poly_to_box(polygens)
                scores = [0.8 + (1-0.8) * np.random.rand() for i in range(len(boxes))]
            else:
                boxes = polygens
                scores = scores
            for box, score in zip(boxes,scores):
                det_header.write('{} {} {} {} {} {}\n'.format(image_path, score, box[0], box[1], box[2], box[3]))
            
            # draw 
            draw_image = draw_polygen(bgr_image, polygens)
            if args.show:
                cv2.imshow('QR Detection', draw_image)
                cv2.waitKey(0)
            
            # save detect image
            if args.save:
                save_full_path = os.path.join(args.root, args.algo, 'det')
                if not os.path.exists(save_full_path):
                    os.makedirs(save_full_path)
                cv2.imwrite(os.path.join(save_full_path, image_path+'.jpg'), draw_image)
    det_header.close()
    
    # calculate recall & precision & AP
    rec, prec, ap = voc_eval(os.path.join(args.root, '{}_'+det_file),
                             os.path.join(args.root, args.subdir)+'/{}.xml',
                             os.path.join(args.root, args.imglist_file),
                             args.class_name,
                             args.root+'/')
    
    # plot annotation boxes size distribution 
    annotation_dist = annotations_distribution(os.path.join(args.root, args.subdir)+'/{}.xml',
                                            os.path.join(args.root, args.imglist_file),
                                            args.class_name,
                                            args.root+'/',
                                            args.size,
                                            args.algo,
                                            args.save)
    annotation_dist = dict(sorted(annotation_dist.items()))
    draw_bar(annotation_dist, 
                os.path.join(args.root, args.algo, '{}_anno_dist.png'.format(args.algo)))
    print(annotation_dist)
    # plot detection boxes size distribution
    det_dist = detection_distribution(os.path.join(args.root, '{}_'+det_file), args.class_name, args.size)
    det_dist = dict(sorted(det_dist.items()))
    draw_bar(det_dist, 
                os.path.join(args.root, args.algo, '{}_det_dist.png'.format(args.algo)))
    print(det_dist)
    plt.close()
    

    draw_pr_curve(rec, prec, 
             os.path.join(args.root, args.algo, '{}_{}_PR.png'.format(args.algo, args.class_name)))
    print('ap={}\naverage_time={}\n'.format(ap, total_time/len(imagelists)))


    # # qrcode generation
    # for i in range(1, 14):
    #     qrcode_generate_and_save("test", 
    #                             "./images/generate_qrcode_v{}.png".format(i),
    #                             version=i)
    # image = cv2.imread("images/doctor.png")
    # qrcode_with_image(image, 'main doctor', './images/doctor_qrcode.png', 
    #                   img_post=(420,185), qrcode_size=(35,30))


    