# import onnx
# onnx_model = onnx.load("ship_detection.onnx")
# onnx.checker.check_model(onnx_model)

import cv2
import numpy as np

def preprocess(img_path, input_size):
    ori_img = cv2.imread(img_path)

    ori_height, ori_width, _ = ori_img.shape

    resize_ratio = input_size / max(ori_height, ori_width)
    resize_width = int(ori_width * resize_ratio)
    resize_height = int(ori_height * resize_ratio)
    resize_image = cv2.resize(ori_img, (resize_width, resize_height))

    padding_left = (input_size - resize_width) // 2
    padding_top = (input_size - resize_height) // 2

    image = cv2.cvtColor(resize_image, cv2.COLOR_BGR2RGB)

    padding_img = np.ones([input_size, input_size, 3], dtype=np.float32) * 128
    padding_img[padding_top:padding_top+resize_height, padding_left:padding_left+resize_width, :] = image

    image = padding_img.transpose([2, 0, 1])[None, ...].astype(np.float32) / 255.

    return image, ori_img, resize_ratio, padding_left, padding_top, ori_height, ori_width

def grid(height, width, mode='xy'):
    ys = np.arange(0, height)
    xs = np.arange(0, width)

    offset_x, offset_y = np.meshgrid(xs, ys)
    offset_yx = np.stack([offset_x, offset_y]).transpose([1, 2, 0])

    if mode == 'xy':
        offset_xy = offset_yx.transpose([1, 0, 2])
        return offset_xy

    return offset_yx

def xywh2xyxy(xywh):
    xyxy = np.copy(xywh)
    xyxy[:, 0] = xywh[:, 0] - xywh[:, 2] / 2  # top left x
    xyxy[:, 1] = xywh[:, 1] - xywh[:, 3] / 2  # top left y
    xyxy[:, 2] = xywh[:, 0] + xywh[:, 2] / 2  # bottom right x
    xyxy[:, 3] = xywh[:, 1] + xywh[:, 3] / 2  # bottom right y
    return xyxy

def non_max_suppression_cv2(prediction, conf_thres=0.25, iou_thres=0.45, max_det=300):
    max_wh = 4096
    max_nms = 30000  # maximum number of boxes into torchvision.ops.nms()

    prediction = prediction[prediction[:, 4] > conf_thres]


    if len(prediction) == 0:
        return np.zeros([0, 6])

    prediction[:, 5:] *= prediction[:, 4:5]  # conf = obj_conf * cls_conf
    categories = np.argmax(prediction[:, 5:], axis=1).reshape([-1, 1])
    scores = np.max(prediction[:, 5:], axis=1, keepdims=True)

    keep = prediction[:, 4] > conf_thres
    prediction = prediction[keep, :5] # x, y, x, y, [conf or obj_conf * cls_conf]
    categories = categories[keep, :]

    if len(prediction) == 0:
        return np.zeros([0, 6])

    prediction = np.concatenate([prediction, categories], axis=1) # x, y, x, y, [conf or obj_conf * cls_conf], category_idx

    if prediction.shape[0] > max_nms:
        # sort by confidence
        prediction = prediction[prediction[:, 4].argsort(descending=True)[:max_nms]]

    # To increase the coordinate gap for different categories
    coordinate_gap = prediction[:, 5:6] * max_wh
    boxes, scores = prediction[:, :4] + coordinate_gap, prediction[:, 4]

    nms_mask = cv2.dnn.NMSBoxes(boxes.tolist(), scores.tolist(), conf_thres, iou_thres)
    nms_mask = np.array(nms_mask).reshape([-1])

    if nms_mask.shape[0] > max_det:  # limit detections
        nms_mask = nms_mask[:max_det]

    output = prediction[nms_mask]

    return output


def sigmoid(x):
    return 1.0 / (1 + np.exp(-x))

def postProcess(predict_layers, strides, anchors, conf_thres, iou_thres, resize_ratio, padding_left, padding_top, ori_width, ori_height):
    '''
    :param predict_layers: [head_small, head_medium, head_large]
    :param strides:
    :param anchors:
    :return:
    '''
    ori_predict = []
    for layer_idx in range(len(predict_layers)):
        predict = predict_layers[layer_idx]
        anchor = anchors[layer_idx]
        num_anchors = anchor.shape[0]
        stride = strides[layer_idx]

        bs, c, h, w = predict.shape
        num_classes = c // num_anchors - 5

        predict = predict.transpose([0, 2, 3, 1]).reshape([bs, h, w, num_anchors, -1])

        grid_xy = grid(height=h, width=w, mode='yx')[None, :, :, None, :] # torch.Size([1, 9, 9, 1, 2])
        anchor_wh = anchor[None, None, None, ...]  # torch.Size([1, 1, 1, 3, 2])

        predict[..., 0:2] = (sigmoid(predict[..., 0:2]) * 2 - 0.5 + grid_xy) * stride
        predict[..., 2:4] = (sigmoid(predict[..., 2:4]) * 2) ** 2 * anchor_wh * stride
        predict[..., 4:5] = sigmoid(predict[..., 4:5])
        predict[..., 5:] = sigmoid(predict[..., 5:])
        predict = predict.reshape(-1, num_classes + 5)

        # predict[..., 0:2] = (sigmoid(predict[..., 0:2]) + grid_xy) * stride
        # predict[..., 2:4] = (np.exp(predict[..., 2:4]) * anchor_wh) * stride
        # predict[..., 4:5] = sigmoid(predict[..., 4:5])
        # predict[..., 5:] = sigmoid(predict[..., 5:])
        # predict = predict.reshape(-1, num_classes + 5)

        predict[:, 0] = (predict[:, 0] - padding_left) / resize_ratio
        predict[:, 1] = (predict[:, 1] - padding_top) / resize_ratio
        predict[:, 2] = predict[:, 2] / resize_ratio
        predict[:, 3] = predict[:, 3] / resize_ratio

        predict[:, 0] = predict[:, 0].clip(0, ori_width - 1)
        predict[:, 1] = predict[:, 1].clip(0, ori_height - 1)
        predict[:, 2] = predict[:, 2].clip(0, ori_width)
        predict[:, 3] = predict[:, 3].clip(0, ori_height)

        keep = (predict[..., 2] > 5) & (predict[..., 3] > 5)
        predict = predict[keep, :]

        predict[:, 0:4] = xywh2xyxy(predict[:, 0:4])
        predict[:, 0] = predict[:, 0].clip(0, ori_width - 1)
        predict[:, 1] = predict[:, 1].clip(0, ori_height - 1)
        predict[:, 2] = predict[:, 2].clip(0, ori_width - 1)
        predict[:, 3] = predict[:, 3].clip(0, ori_height - 1)

        ori_predict.append(predict)
    ori_predict = np.concatenate(ori_predict, axis=0)

    # results = non_max_suppression(ori_predict, conf_thres=conf_thres, iou_thres=iou_thres, max_det=300)
    results = non_max_suppression_cv2(ori_predict, conf_thres=conf_thres, iou_thres=iou_thres, max_det=300)


    boxes = results[:, :4]
    scores = results[:, 4:5]
    categories = results[:, 5:6]

    return scores, categories, boxes

def get_color(idx, bgr=True):

    def hex2rgb(h):
        return tuple(int(h[1 + i:1 + i + 2], 16) for i in (0, 2, 4))

    hex = ('FF3838', 'FF9D97', 'FF701F', 'FFB21D', 'CFD231', '48F90A', '92CC17', '3DDB86', '1A9334', '00D4BB', '2C99A8', '00C2FF', '344593', '6473FF', '0018EC', '8438FF', '520085', 'CB38FF', 'FF95C8', 'FF37C7')

    palette = [hex2rgb('#' + c) for c in hex]
    n = len(palette)

    c = palette[int(idx) % n]

    return (c[2], c[1], c[0]) if bgr else c

def draw_box_label(image, box, text='', line_width=2, line_color=(128, 128, 128), font_size=1, font_color=(255, 255, 255), bgr=True):
    '''
    :param image:
    :param box: xyxy
    :param text:
    :param line_width:
    :param line_color: int or BGR color
    :param font_size:
    :param font_color:
    :param bgr:
    :return:
    '''
    assert isinstance(image, np.ndarray), f'Type of parameter image must be np.ndaary, not {type(image)}'

    # if isinstance(font_color, int):
    #     font_color = get_color(font_color, bgr=bgr)
    if isinstance(line_color, int):
        line_color = get_color(line_color, bgr=bgr)

    line_width = line_width or round(sum(image.shape[:2]) / 2 * 0.003)

    x_min, y_min, x_max, y_max = box
    p1, p2 = (int(x_min), int(y_min)), (int(x_max), int(y_max))

    image = cv2.rectangle(image, p1, p2, line_color, thickness=line_width, lineType=cv2.LINE_AA)

    if text:
        font_size = font_size or max(line_width - 1, 1)
        font_w, font_h = cv2.getTextSize(text, 0, fontScale=line_width / 3, thickness=font_size)[0]
        outside = int(y_min) - font_h - 3 >= 0
        p2 = (int(x_min) + font_w, int(y_min) - font_h - 3 if outside else p1[1] + font_h + 3)
        image = cv2.rectangle(image, p1, p2, line_color, -1, cv2.LINE_AA)
        image = cv2.putText(image, text, (p1[0], p1[1] - 2 if outside else p1[1] + font_h + 2), 0, line_width / 3, font_color, thickness=font_size, lineType=cv2.LINE_AA)

    return image

import onnxruntime
ort_session = onnxruntime.InferenceSession("u_yolov3.onnx")

from glob import glob
import os
input_size = 640
# image_dir = r'./images'
image_dir = r'S:/datasets/coco2017/val/images'

files = glob(os.path.join(image_dir, '*.jpg'))

for file in files:
    image, ori_img, resize_ratio, padding_left, padding_top, ori_height, ori_width = preprocess(file, input_size)

    ort_inputs = {ort_session.get_inputs()[0].name: image}
    ort_outs = ort_session.run(None, ort_inputs)

    anchors_small = np.array([[116, 90], [156, 198], [373, 326]]) / 32
    anchors_medium = np.array([[30, 61], [62, 45], [59, 119]]) / 16
    anchors_large = np.array([[10, 13], [16, 30], [33, 23]]) / 8
    anchors = (anchors_small, anchors_medium, anchors_large)

    strides = [32, 16, 8]
    conf_thres = 0.25
    iou_thres = 0.45

    scores, categories, boxes = postProcess(ort_outs, strides, anchors, conf_thres, iou_thres, resize_ratio, padding_left, padding_top, ori_width, ori_height)

    for box, category, score in zip(boxes, categories, scores):
        # box = box.to(dtype=torch.int32)
        box.astype(np.int32)
        xmin, ymin, xmax, ymax = box
        ori_img = draw_box_label(ori_img, (xmin, ymin, xmax, ymax), text=str(int(category)), line_color=int(category))
    cv2.imshow('img', ori_img)
    cv2.waitKey()
