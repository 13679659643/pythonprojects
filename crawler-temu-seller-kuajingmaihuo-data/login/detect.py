# -*- coding: utf-8 -*-
# @Time    : 2024/11/14 9:13
# @Author  : Night
# @File    : detect.py
# @Description:
import time
from io import BytesIO
import onnxruntime
import torch
import torchvision
import numpy as np
import cv2
from PIL import Image
from skimage.metrics import structural_similarity as ssim

from login import get_file_path


def padded_resize(im, new_shape=(320, 320), stride=32):
    try:
        shape = im.shape[:2]

        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]
        # dw, dh = np.mod(dw, stride), np.mod(dh, stride)
        dw /= 2
        dh /= 2
        if shape[::-1] != new_unpad:  # resize
            im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114, 114, 114))  # add border
        # Convert
        im = im.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
        im = np.ascontiguousarray(im)
        im = torch.from_numpy(im)
        im = im.float()
        im /= 255
        im = im[None]
        im = im.cpu().numpy()  # torch to numpy
        return im
    except:
        print("123")


def xywh2xyxy(x):
    # Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right
    y = x.clone() if isinstance(x, torch.Tensor) else np.copy(x)
    y[:, 0] = x[:, 0] - x[:, 2] / 2  # top left x
    y[:, 1] = x[:, 1] - x[:, 3] / 2  # top left y
    y[:, 2] = x[:, 0] + x[:, 2] / 2  # bottom right x
    y[:, 3] = x[:, 1] + x[:, 3] / 2  # bottom right y
    return y


def box_iou(box1, box2):
    """
    Return intersection-over-union (Jaccard index) of boxes.
    Both sets of boxes are expected to be in (x1, y1, x2, y2) format.
    Arguments:
        box1 (Tensor[N, 4])
        box2 (Tensor[M, 4])
    Returns:
        iou (Tensor[N, M]): the NxM matrix containing the pairwise
            IoU values for every element in boxes1 and boxes2
    """

    def box_area(box):
        # box = 4xn
        return (box[2] - box[0]) * (box[3] - box[1])

    area1 = box_area(box1.T)
    area2 = box_area(box2.T)

    # inter(N,M) = (rb(N,M,2) - lt(N,M,2)).clamp(0).prod(2)
    inter = (torch.min(box1[:, None, 2:], box2[:, 2:]) - torch.max(box1[:, None, :2], box2[:, :2])).clamp(0).prod(2)
    return inter / (area1[:, None] + area2 - inter)  # iou = inter / (area1 + area2 - inter)


def non_max_suppression(prediction, conf_thres=0.25, iou_thres=0.45, classes=None, agnostic=False, multi_label=False,
                        labels=(), max_det=300):
    """Runs Non-Maximum Suppression (NMS) on inference results

    Returns:
         list of detections, on (n,6) tensor per image [xyxy, conf, cls]
    """

    nc = prediction.shape[2] - 5  # number of classes
    xc = prediction[..., 4] > conf_thres  # candidates

    # Checks
    assert 0 <= conf_thres <= 1, f'Invalid Confidence threshold {conf_thres}, valid values are between 0.0 and 1.0'
    assert 0 <= iou_thres <= 1, f'Invalid IoU {iou_thres}, valid values are between 0.0 and 1.0'

    # Settings
    min_wh, max_wh = 2, 7680  # (pixels) minimum and maximum box width and height
    max_nms = 30000  # maximum number of boxes into torchvision.ops.nms()
    time_limit = 10.0  # seconds to quit after
    redundant = True  # require redundant detections
    multi_label &= nc > 1  # multiple labels per box (adds 0.5ms/img)
    merge = False  # use merge-NMS

    t = time.time()
    output = [torch.zeros((0, 6), device=prediction.device)] * prediction.shape[0]
    for xi, x in enumerate(prediction):  # image index, image inference
        # Apply constraints
        x[((x[..., 2:4] < min_wh) | (x[..., 2:4] > max_wh)).any(1), 4] = 0  # width-height
        x = x[xc[xi]]  # confidence

        # Cat apriori labels if autolabelling
        if labels and len(labels[xi]):
            lb = labels[xi]
            v = torch.zeros((len(lb), nc + 5), device=x.device)
            v[:, :4] = lb[:, 1:5]  # box
            v[:, 4] = 1.0  # conf
            v[range(len(lb)), lb[:, 0].long() + 5] = 1.0  # cls
            x = torch.cat((x, v), 0)

        # If none remain process next image
        if not x.shape[0]:
            continue

        # Compute conf
        x[:, 5:] *= x[:, 4:5]  # conf = obj_conf * cls_conf

        # Box (center x, center y, width, height) to (x1, y1, x2, y2)
        box = xywh2xyxy(x[:, :4])

        # Detections matrix nx6 (xyxy, conf, cls)
        if multi_label:
            i, j = (x[:, 5:] > conf_thres).nonzero(as_tuple=False).T
            x = torch.cat((box[i], x[i, j + 5, None], j[:, None].float()), 1)
        else:  # best class only
            conf, j = x[:, 5:].max(1, keepdim=True)
            x = torch.cat((box, conf, j.float()), 1)[conf.view(-1) > conf_thres]

        # Filter by class
        if classes is not None:
            x = x[(x[:, 5:6] == torch.tensor(classes, device=x.device)).any(1)]

        # Apply finite constraint
        # if not torch.isfinite(x).all():
        #     x = x[torch.isfinite(x).all(1)]

        # Check shape
        n = x.shape[0]  # number of boxes
        if not n:  # no boxes
            continue
        elif n > max_nms:  # excess boxes
            x = x[x[:, 4].argsort(descending=True)[:max_nms]]  # sort by confidence

        # Batched NMS
        c = x[:, 5:6] * (0 if agnostic else max_wh)  # classes
        boxes, scores = x[:, :4] + c, x[:, 4]  # boxes (offset by class), scores
        i = torchvision.ops.nms(boxes, scores, iou_thres)  # NMS
        if i.shape[0] > max_det:  # limit detections
            i = i[:max_det]
        if merge and (1 < n < 3E3):  # Merge NMS (boxes merged using weighted mean)
            # update boxes as boxes(i,4) = weights(i,n) * boxes(n,4)
            iou = box_iou(boxes[i], boxes) > iou_thres  # iou matrix
            weights = iou * scores[None]  # box weights
            x[i, :4] = torch.mm(weights, x[:, :4]).float() / weights.sum(1, keepdim=True)  # merged boxes
            if redundant:
                i = i[iou.sum(1) > 1]  # require redundancy

        output[xi] = x[i]
        if (time.time() - t) > time_limit:
            break  # time limit exceeded

    return output


def xyxy2xywh(x):
    # Convert nx4 boxes from [x1, y1, x2, y2] to [x, y, w, h] where xy1=top-left, xy2=bottom-right
    y = x.clone() if isinstance(x, torch.Tensor) else np.copy(x)
    y[:, 0] = (x[:, 0] + x[:, 2]) / 2  # x center
    y[:, 1] = (x[:, 1] + x[:, 3]) / 2  # y center
    y[:, 2] = x[:, 2] - x[:, 0]  # width
    y[:, 3] = x[:, 3] - x[:, 1]  # height
    return y


def is_ascii(s=''):
    # Is string composed of all ASCII (no UTF) characters? (note str().isascii() introduced in python 3.7)
    s = str(s)  # convert list, tuple, None, etc. to str
    return len(s.encode().decode('ascii', 'ignore')) == len(s)


def box_label(self, box, label='', color=(128, 128, 128), txt_color=(255, 255, 255)):
    # Add one xyxy box to image with label
    if self.pil or not is_ascii(label):
        self.draw.rectangle(box, width=self.lw, outline=color)  # box
        if label:
            w, h = self.font.getsize(label)  # text width, height
            outside = box[1] - h >= 0  # label fits outside box
            self.draw.rectangle((box[0],
                                 box[1] - h if outside else box[1],
                                 box[0] + w + 1,
                                 box[1] + 1 if outside else box[1] + h + 1), fill=color)
            # self.draw.text((box[0], box[1]), label, fill=txt_color, font=self.font, anchor='ls')  # for PIL>8.0
            self.draw.text((box[0], box[1] - h if outside else box[1]), label, fill=txt_color, font=self.font)
    else:  # cv2
        p1, p2 = (int(box[0]), int(box[1])), (int(box[2]), int(box[3]))
        cv2.rectangle(self.im, p1, p2, color, thickness=self.lw, lineType=cv2.LINE_AA)
        if label:
            tf = max(self.lw - 1, 1)  # font thickness
            w, h = cv2.getTextSize(label, 0, fontScale=self.lw / 3, thickness=tf)[0]  # text width, height
            outside = p1[1] - h - 3 >= 0  # label fits outside box
            p2 = p1[0] + w, p1[1] - h - 3 if outside else p1[1] + h + 3
            cv2.rectangle(self.im, p1, p2, color, -1, cv2.LINE_AA)  # filled
            cv2.putText(self.im, label, (p1[0], p1[1] - 2 if outside else p1[1] + h + 2), 0, self.lw / 3, txt_color,
                        thickness=tf, lineType=cv2.LINE_AA)


def return_coordinates(xyxy, conf):
    conf = float(conf.numpy())
    gain = 1.02
    pad = 10
    xyxy = torch.tensor(xyxy).view(-1, 4)
    b = xyxy2xywh(xyxy)  # boxes
    b[:, 2:] = b[:, 2:] * gain + pad  # box wh * gain + pad
    xyxy = xywh2xyxy(b).long()
    c1, c2 = (int(xyxy[0, 0]) + 6, int(xyxy[0, 1]) + 6), (int(xyxy[0, 2]) - 6, int(xyxy[0, 3]) - 6)
    # print(f"leftTop:{c1},rightBottom:{c2},Confidence:{conf*100}%")
    result_dict = {"leftTop": c1, "rightBottom": c2, "Confidence": conf}
    return result_dict


def clip_coords(boxes, shape):
    # Clip bounding xyxy bounding boxes to image shape (height, width)
    if isinstance(boxes, torch.Tensor):  # faster individually
        boxes[:, 0].clamp_(0, shape[1])  # x1
        boxes[:, 1].clamp_(0, shape[0])  # y1
        boxes[:, 2].clamp_(0, shape[1])  # x2
        boxes[:, 3].clamp_(0, shape[0])  # y2
    else:  # np.array (faster grouped)
        boxes[:, [0, 2]] = boxes[:, [0, 2]].clip(0, shape[1])  # x1, x2
        boxes[:, [1, 3]] = boxes[:, [1, 3]].clip(0, shape[0])  # y1, y2


def scale_coords(img1_shape, coords, img0_shape, ratio_pad=None):
    # Rescale coords (xyxy) from img1_shape to img0_shape
    if ratio_pad is None:  # calculate from img0_shape
        gain = min(img1_shape[0] / img0_shape[0], img1_shape[1] / img0_shape[1])  # gain  = old / new
        pad = (img1_shape[1] - img0_shape[1] * gain) / 2, (img1_shape[0] - img0_shape[0] * gain) / 2  # wh padding
    else:
        gain = ratio_pad[0][0]
        pad = ratio_pad[1]

    coords[:, [0, 2]] -= pad[0]  # x padding
    coords[:, [1, 3]] -= pad[1]  # y padding
    coords[:, :4] /= gain
    clip_coords(coords, img0_shape)
    return coords


def detect_edges(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours


def extract_region(image, coordinate, width=60):
    x1, y1 = coordinate['leftTop']
    x2 = x1 + width
    y2 = coordinate['rightBottom'][1]

    # Add padding to the region
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(image.shape[1], x2)
    y2 = min(image.shape[0], y2)

    return image[y1:y2, x1:x2]


def onnx_model_main(path):
    # onnx
    session = onnxruntime.InferenceSession(get_file_path("best.onnx"), providers=["CPUExecutionProvider"])
    start = time.time()
    image = open(path, "rb").read()
    img = np.array(Image.open(BytesIO(image)))
    img = img[:, :, :3]
    im = padded_resize(img)
    pred = session.run([session.get_outputs()[0].name], {session.get_inputs()[0].name: im})[0]
    pred = torch.tensor(pred)
    pred = non_max_suppression(pred, conf_thres=0.60, iou_thres=0.60, max_det=1000)

    coordinate_list = []
    for i, det in enumerate(pred):
        det[:, :4] = scale_coords(im.shape[2:], det[:, :4], img.shape).round()
        for *xyxy, conf, cls in reversed(det):
            coordinates = return_coordinates(xyxy, conf)
            region = extract_region(img, coordinates)
            contours = detect_edges(region)
            coordinates['contours'] = contours
            coordinate_list.append(coordinates)

    # Sort coordinates by confidence and select top two
    coordinate_list = sorted(coordinate_list, key=lambda a: a["Confidence"], reverse=True)

    duration = str((time.time() - start))
    if len(coordinate_list) < 2:
        data = {'message': 'error', 'time': duration}
        return []
    else:
        # Get top two coordinates
        coordinate1 = coordinate_list[0]
        coordinate2 = coordinate_list[1]

        # Prepare data for two coordinates
        data = {
            'message': 'success',
            'time': duration,
            'coordinates': [
                {
                    'point': f"{coordinate1['leftTop'][0]}|{coordinate1['leftTop'][1]}|{coordinate1['rightBottom'][0] - coordinate1['leftTop'][0]}|{coordinate1['rightBottom'][1] - coordinate1['leftTop'][1]}",
                    **coordinate1
                },
                {
                    'point': f"{coordinate2['leftTop'][0]}|{coordinate2['leftTop'][1]}|{coordinate2['rightBottom'][0] - coordinate2['leftTop'][0]}|{coordinate2['rightBottom'][1] - coordinate2['leftTop'][1]}",
                    **coordinate2
                }
            ]
        }
        trace_list = []
        for i in data['coordinates']:
            trace_list.append(i['point'])
        return trace_list


def drow_rectangle(coordinate_data, path):
    img = cv2.imread(path)
    # Draw rectangles for each coordinate
    for coordinate in coordinate_data.get('coordinates', []):
        cv2.rectangle(img, coordinate.get("leftTop"), coordinate.get("rightBottom"), (0, 0, 255), 2)
    cv2.imwrite("drow_recta"
                "ngle.jpg", img)
    print("返回坐标矩形成功")


def calculate_similarity(patch_img, bg_crop):
    """
    计算缺口图和背景图裁剪部分的相似度
    :param patch_img: 缺口图
    :param bg_crop: 背景图裁剪部分
    :return: 相似度评分
    """
    # 将图像转换为灰度图像
    patch_gray = cv2.cvtColor(patch_img, cv2.COLOR_BGR2GRAY)
    bg_gray = cv2.cvtColor(bg_crop, cv2.COLOR_BGR2GRAY)

    # 获取图像的最小维度
    min_dim = min(patch_gray.shape)

    # 设置 win_size 为最小维度减一，确保不超过图像尺寸
    win_size = min(min_dim, 7)  # 默认值为7，但不能超过图像的最小维度

    # 使用SSIM (Structural Similarity Index) 方法计算相似度
    score = ssim(patch_gray, bg_gray, win_size=win_size, full=False, multichannel=False)
    return score


def preprocess_image(image):
    """对输入图像进行预处理"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # 转换为灰度图
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)  # 二值化
    kernel = np.ones((3, 3), np.uint8)
    opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)  # 形态学开运算去除噪声
    sure_bg = cv2.dilate(opening, kernel, iterations=3)  # 膨胀背景
    dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)  # 距离变换
    ret, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)  # 阈值分割前景
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg, sure_fg)  # 找到不确定区域
    return sure_fg, unknown


def extract_contours(image):
    """从图像中提取轮廓"""
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours


def contour_similarity(contour1, contour2):
    """计算两个轮廓的相似度"""
    ret = cv2.matchShapes(contour1, contour2, cv2.CONTOURS_MATCH_I1, 0.0)
    return ret


def find_target_gap(coordinate_onnx, bg_path, patch_path):
    # 读取背景图和缺口图
    bg = cv2.imread(bg_path)
    patch = cv2.imread(patch_path)

    # 将缺口图调整为实际大小 (60, 56)
    patch = cv2.resize(patch, (60, 56))

    # 对背景图和缺口图进行预处理
    bg_processed, _ = preprocess_image(bg)
    patch_processed, _ = preprocess_image(patch)

    # 提取缺口图的轮廓
    patch_contours = extract_contours(patch_processed)

    max_similarity = -float('inf')
    target_position = None

    for coord in coordinate_onnx:
        x, y, w, h = map(int, coord.split('|'))

        # 提取背景图中的潜在缺口区域，并进行预处理
        roi = bg[y:y + h, x:x + w]
        roi_processed, _ = preprocess_image(roi)

        # 确保 ROI 和 patch 大小一致
        if roi_processed.shape[:2] != patch_processed.shape[:2]:
            roi_processed = cv2.resize(roi_processed, (patch_processed.shape[1], patch_processed.shape[0]))

        # 提取潜在缺口区域的轮廓
        roi_contours = extract_contours(roi_processed)

        # 计算轮廓相似度
        contour_sim = 0.0
        if len(roi_contours) > 0 and len(patch_contours) > 0:
            contour_sim = contour_similarity(roi_contours[0], patch_contours[0])

        # 计算像素相似度 (使用均方误差的负值作为相似度)
        mse = np.mean((roi_processed.astype("float") - patch_processed.astype("float")) ** 2)
        pixel_sim = -mse

        # 综合评估相似度
        combined_sim = contour_sim + pixel_sim

        if combined_sim > max_similarity:
            max_similarity = combined_sim
            target_position = (x, y)

    return target_position[0]


if __name__ == '__main__':
    bg_path = 'bg.png'
    patch_path = 'patch.png'
    coordinate_onnx = onnx_model_main(bg_path)
    target_gap = find_target_gap(coordinate_onnx, bg_path, patch_path)
    print(target_gap)
