import os
import cv2
import logging
import numpy as np
import pickle as pk
from interval import Interval
logger = logging.getLogger(__name__)


from voc_eval import parse_rec
from draw import draw_polygen

def annotations_distribution(annopath,
             imagesetfile,
             classname,
             cachedir,
             size_group,
             algo_name,
             save_anno=False):
    # first load gt
    if not os.path.isdir(cachedir):
        os.mkdir(cachedir)
    imageset = os.path.splitext(os.path.basename(imagesetfile))[0]
    cachefile = os.path.join(cachedir, imageset + '_annots.pkl')
    # read list of images
    with open(imagesetfile, 'r') as f:
        lines = f.readlines()
    imagenames = [x.strip() for x in lines]

    if not os.path.isfile(cachefile):
        # load annots
        recs = {}
        for i, imagename in enumerate(imagenames):
            recs[imagename] = parse_rec(annopath.format(imagename))
            if i % 100 == 0:
                logger.info(
                    'Reading annotation for {:d}/{:d}'.format(
                        i + 1, len(imagenames)))
        # save
        logger.info('Saving cached annotations to {:s}'.format(cachefile))
        with open(cachefile, 'wb') as f:
            pk.dump(recs, f)
    else:
        # load
        with open(cachefile, 'rb') as f:
            recs = pk.load(f)

    #
    image_root = annopath[:annopath.rfind('/')]
    # extract gt objects for this class
    key, value = init_distribution(size_group)

    box_dist = {}
    for imagename in imagenames:
        image_path = os.path.join(os.path.dirname(image_root), algo_name, 'det', imagename + '.jpg')
        if not os.path.exists(image_path):
            image_path = os.path.join(image_root, imagename + '.jpg')
        bgr_image = cv2.imread(image_path)
        R = [obj for obj in recs[imagename] if obj['name'] == classname]
        bbox = [x['bbox'] for x in R]
        if save_anno:
            save_path = os.path.join(os.path.dirname(image_root), algo_name, 'det+anno')
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            draw_image = draw_polygen(bgr_image, bbox, (0, 0, 255))
            cv2.imwrite(os.path.join(save_path, imagename + '.jpg'), draw_image)

        for idx in range(len(bbox)):
            box = bbox[idx]
            size = int(min(box[2] - box[0], box[3] - box[1]))
            for j in range(len(value)):
                if size in value[j]:
                    if key[j] in box_dist.keys():
                        box_dist[key[j]] += 1
                    else:
                        box_dist[key[j]] = 1
                    break
    return box_dist


def detection_distribution(detpath, classname, size_group):
    detfile = detpath.format(classname)
    with open(detfile, 'r') as f:
        lines = f.readlines()
    splitlines = [x.strip().split(' ') for x in lines]
    BB = np.array([[float(z) for z in x[2:]] for x in splitlines])

    key, value = init_distribution(size_group)
    
    box_dist = {}
    bbox = BB
    for i in range(bbox.shape[0]):
        box = bbox[i, :]
        size = int(min(box[2] - box[0], box[3] - box[1]))
        for j in range(len(value)):
            if size in value[j]:
                if key[j] in box_dist.keys():
                    box_dist[key[j]] += 1
                else:
                    box_dist[key[j]] = 1
                break
    return box_dist


def init_distribution(size_group):
    key = []
    value = []
    size_group = sorted(size_group)
    size_len = len(size_group)
    for idx in range(size_len):
        inter = None
        inter_last = None
        if 0 == idx:
            inter = Interval(0, size_group[idx], lower_closed=False)
        elif size_len-1 == idx:
            inter_last = Interval(size_group[size_len-1], float('inf'), closed=False)
            inter = Interval(size_group[size_len-2], size_group[size_len-1], lower_closed=False)
        else:
            inter = Interval(size_group[idx-1], size_group[idx], lower_closed=False)
        if inter:
            key.append(str(inter))
            value.append(inter)
        if inter_last:
            key.append(str(inter_last))
            value.append(inter_last)
    return key, value