import os
import cv2
import uuid
import argparse
import numpy as np
from tqdm import tqdm


from utils.files import get_file_list, read_file, write_file
from utils.template_augment import collect_templates, replace_paste, random_paste, iou_paste

def args_parse():
    parser = argparse.ArgumentParser(description='Manual data augmentation.')
    parser.add_argument('--src-data', type=str, default='', help='Data used for data augmentation.')
    parser.add_argument('--template-data', type=str, default='', help='Template images')
    parser.add_argument('--target-data', type=str, default='', help='Path for saving augmentation data')
    parser.add_argument('--ratio-res-thr', type=float, default=0.5, help='ratio res threshold for replace paste')
    parser.add_argument('--ratio-thr', type=float, default=0.3, help='ratio threshold for replace paste')
    parser.add_argument('--iou-thr', type=float, default=0.5, help='iou threshold for random & iou paste')
    parser.add_argument('--debug-dir', type=str, default='', help='Path for saving debug info')
    parser.add_argument(
        '--noise-type', 
        type=str, 
        default='None', 
        choices=['None', 'gaussian', 'saltpepper', 'poisson', 'uniform'], 
        help='noise type')
    parser.add_argument(
        '--pad',
        action='store_true', 
        help='If pad the box label.'
    )
    parser.add_argument('--pad-ratio', type=float, default=0.005, help='pad box label according to ratio')
    parser.add_argument('--pad-max-pixel', type=int, default=5, help='max pixel value of pad')
    return parser.parse_args()


def save_augment(aug_image, aug_labels, root, name):
    """
    """
    uuid_str = str(uuid.uuid1())
    aug_image_path = os.path.join(root, 
                                  name + '-' + uuid_str + '.png')
    aug_label_path = os.path.join(root,
                                  name + '-' + uuid_str + '.txt')
    cv2.imwrite(aug_image_path, aug_image)
    write_file(aug_label_path, aug_labels)


def do_augment(src_data, template_data, target_data, ratio_res_thr, 
               ratio_thr, iou_thr, noise_type, debug_dir, aug_count=1):
    """
    """
    # src dataset
    if not os.path.exists(src_data):
        print("{} not exists, please check".format(src_data))
        return
    imagelists = get_file_list(src_data, type='image')

    # templates 
    template_images = collect_templates(template_data, ratio_thr, noise_type, debug_dir)

    # target 
    if not os.path.exists(target_data):
        os.makedirs(target_data)

    for count in range(aug_count):
        # iter src
        process_bar = tqdm(imagelists)
        for image_file in process_bar:
            # src data info
            image_name = os.path.splitext(image_file)[0]
            label_file = image_name + ".txt"
            image = cv2.imread(os.path.join(src_data, image_file))

            if os.path.exists(os.path.join(src_data, label_file)):
                labels = read_file(os.path.join(src_data, label_file))
            else:
                labels = None

            # do augmentation
            aug_types = ['replace', 'random', 'iou']
            aug_type = aug_types[np.random.randint(len(aug_types))]
            if aug_type in ['replace', 'iou'] and labels is None:
                continue
            if aug_type == 'replace':
                aug_image, aug_labels = replace_paste(image, labels, template_images, ratio_res_thr, ratio_thr)
            if aug_type == 'random':
                aug_image, aug_labels = random_paste(image, template_images, iou_thr)
            if aug_type == 'iou':
                aug_image, aug_labels = iou_paste(image, labels, template_images, iou_thr)

            # save augmentation
            if len(aug_labels) != 0:
                save_augment(aug_image, aug_labels, target_data, image_name)
            else:
                print('replace fail, please check ratio thr')


if __name__ == "__main__":
    args = args_parse()
    print(args)

    if os.path.isdir(args.debug_dir) and not os.path.exists(args.debug_dir):
        os.makedirs(args.debug_dir)

    do_augment(args.src_data,
               args.template_data,
               args.target_data,
               args.ratio_res_thr,
               args.ratio_thr,
               args.iou_thr,
               args.noise_type,
               args.debug_dir)
    







