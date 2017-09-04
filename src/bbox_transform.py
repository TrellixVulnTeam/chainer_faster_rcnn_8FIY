import numpy as np
import random

# Example ROIs: (xa_1, ya_1, xa_2, ya_2)
# Ground-truth ROIS: (x*_1, y*_1, x*_2, y*_2)
# Return (t*_x, t*_y, t*_w, t*_h)
def bbox_transform(ex_rois, gt_rois):
    ex_widths = ex_rois[:, 2] - ex_rois[:, 0] + 1.
    ex_heights = ex_rois[:, 3] - ex_rois[:, 1] + 1.
    ex_ctr_x = ex_rois[:, 0] + 0.5 * ex_widths
    ex_ctr_y = ex_rois[:, 1] + 0.5 * ex_heights

    gt_widths = gt_rois[:, 2] - gt_rois[:, 0] + 1.
    gt_heights = gt_rois[:, 3] - gt_rois[:, 1] + 1.
    gt_ctr_x = gt_rois[:, 0] + 0.5 * gt_widths
    gt_ctr_y = gt_rois[:, 1] + 0.5 * gt_heights

    targets_dx = (gt_ctr_x - ex_ctr_x) / ex_widths
    targets_dy = (gt_ctr_y - ex_ctr_y) / ex_heights
    targets_dw = np.log(gt_widths / ex_widths)
    targets_dh = np.log(gt_heights / ex_heights)

    targets = np.vstack((targets_dx, targets_dy, targets_dw, targets_dh)).transpose()
    return targets

def bbox_transform_inv(anchors, deltas):
    if anchors.shape[0] == 0:
        return np.zeros((0, deltas.shape[1]), dtype=deltas.dtype)

    anchors = anchors.astype(deltas.dtype, copy=False)

    anchor_widths = anchors[:, 2] - anchors[:, 0] + 1.
    anchor_heights = anchors[:, 3] - anchors[:, 1] + 1.
    anchor_ctr_x = anchors[:, 0] + 0.5 * anchor_widths
    anchor_ctr_y = anchors[:, 1] + 0.5 * anchor_heights

    dx = deltas[:, 0::4]
    dy = deltas[:, 1::4]
    dw = deltas[:, 2::4]
    dh = deltas[:, 3::4]

    pred_ctr_x = dx * anchor_widths[:, np.newaxis] + anchor_ctr_x[:, np.newaxis]
    pred_ctr_y = dy * anchor_heights[:, np.newaxis] + anchor_ctr_y[:, np.newaxis]
    pred_w = np.exp(dw) * anchor_widths[:, np.newaxis]
    pred_h = np.exp(dh) * anchor_heights[:, np.newaxis]

    pred_boxes = np.zeros(deltas.shape, dtype=deltas.dtype)
    pred_boxes[:, 0::4] = pred_ctr_x - 0.5 * pred_w
    pred_boxes[:, 1::4] = pred_ctr_y - 0.5 * pred_h
    pred_boxes[:, 2::4] = pred_ctr_x + 0.5 * pred_w
    pred_boxes[:, 3::4] = pred_ctr_y + 0.5 * pred_h

    return pred_boxes

def clip_boxes(boxes, im_shape):
    boxes[:, 0::4] = np.maximum(np.minimum(boxes[:, 0::4], im_shape[1] - 1), 0)
    boxes[:, 1::4] = np.maximum(np.minimum(boxes[:, 1::4], im_shape[0] - 1), 0)
    boxes[:, 2::4] = np.maximum(np.minimum(boxes[:, 2::4], im_shape[1] - 1), 0)
    boxes[:, 3::4] = np.maximum(np.minimum(boxes[:, 3::4], im_shape[0] - 1), 0)
    return boxes

def resize_bbox(bbox, in_size, out_size):
    print(bbox.shape)
    bbox = bbox.copy()
    y_scale = float(out_size[0] / in_size[0])
    x_scale = float(out_size[1] / in_size[1])
    bbox[:, 0] = y_scale * bbox[:, 0]
    bbox[:, 2] = y_scale * bbox[:, 2]
    bbox[:, 1] = x_scale * bbox[:, 1]
    bbox[:, 3] = x_scale * bbox[:, 3]
    return bbox

def flip_bbox(bbox, size, y_flip=False, x_flip=False):
    H, W = size
    bbox = bbox.copy()
    if y_flip:
        y_max = H - 1 - bbox[:, 0]
        y_min = H - 1 - bbox[:, 2]
        bbox[:, 0] = y_min
        bbox[:, 2] = y_max
    if x_flip:
        x_max = W - 1 - bbox[:, 1]
        x_min = W - 1 - bbox[:, 3]
        bbox[:, 1] = x_min
        bbox[:, 3] = x_max
    return bbox

def random_flip(img, y_random=False, x_random=False,
                return_param=False, copy=False):
    y_flip, x_flip = False, False
    if y_random:
        y_flip = random.choice([True, False])
    if x_random:
        x_flip = random.choice([True, False])

    if y_flip:
        img = img[:, ::-1, :]
    if x_flip:
        img = img[:, :, ::-1]

    if copy:
        img = img.copy()

    if return_param:
        return img, {'y_flip': y_flip, 'x_flip': x_flip}
    else:
        return img
