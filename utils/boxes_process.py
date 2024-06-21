import torch
import numpy as np

def compute_iou(box1, box2, mode='Minimum'):
    '''Compute the intersection over union of two set of boxes, each box is [x1,y1,x2,y2].
    Args:
        box1: (tensor) bounding boxes, sized [N,4].
        box2: (tensor) bounding boxes, sized [M,4].
    Return:
        (tensor) iou, sized [N,M].
    '''
    N = box1.size(0)
    M = box2.size(0)

    lt = torch.max(
        box1[:,:2].unsqueeze(1).expand(N,M,2),  # [N,2] -> [N,1,2] -> [N,M,2]
        box2[:,:2].unsqueeze(0).expand(N,M,2),  # [M,2] -> [1,M,2] -> [N,M,2]
    )

    rb = torch.min(
        box1[:,2:].unsqueeze(1).expand(N,M,2),  # [N,2] -> [N,1,2] -> [N,M,2]
        box2[:,2:].unsqueeze(0).expand(N,M,2),  # [M,2] -> [1,M,2] -> [N,M,2]
    )

    wh = rb - lt  # [N,M,2]
    wh[wh<0] = 0  # clip at 0
    inter = wh[:,:,0] * wh[:,:,1]  # [N,M]

    area1 = (box1[:,2]-box1[:,0]) * (box1[:,3]-box1[:,1])  # [N,]
    area2 = (box2[:,2]-box2[:,0]) * (box2[:,3]-box2[:,1])  # [M,]
    area1 = area1.unsqueeze(1).expand_as(inter)  # [N,] -> [N,1] -> [N,M]
    area2 = area2.unsqueeze(0).expand_as(inter)  # [M,] -> [1,M] -> [N,M]
    if mode == 'Union':
        iou = inter / (area1 + area2 - inter)
    if mode == 'Minimum':
        iou = inter / (np.minimum(area1, area2))
    return iou


def poly_to_box(polygens):
    if polygens is not None:
        assert len(polygens.shape) == 3, 'polygens must be 3-dims.'
        polygens = polygens.astype(int)
        left_top = np.min(polygens, axis=1)
        right_down = np.max(polygens, axis=1)
        boxes = []
        for idx in range(polygens.shape[0]):
            boxes.append([left_top[idx][0], left_top[idx][1], right_down[idx][0], right_down[idx][1]])
        return boxes
    else:
        print('Polygens is null.')
        return []