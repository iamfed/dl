"""
对数据集中的图像进行分割
"""
from PIL import Image
import os
import cv2
import numpy as np
from torchvision import transforms
from PIL import Image
import torch
import gc
from tqdm import tqdm
gc.collect()
torch.cuda.empty_cache()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def YCrCb(source, target):
    try:
        img = cv2.imread(source)

        # converting from gbr to YCbCr color space
        img_YCrCb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)

        # skin color range for hsv YCbCr space
        YCrCb_mask = cv2.inRange(img_YCrCb, (0, 135, 85), (255, 180, 135))
        # YCrCb_mask = cv2.inRange(img_YCrCb, (0, 0, 20), (234, 23, 10))
        YCrCb_mask = cv2.medianBlur(YCrCb_mask, 7)
        YCrCb_mask = cv2.morphologyEx(
            YCrCb_mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        YCrCb_mask = cv2.morphologyEx(
            YCrCb_mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))

        YCrCb_result = cv2.bitwise_not(YCrCb_mask)
        # 抠图
        # global_result = cv2.bitwise_and(img, img, mask=global_mask)

        cv2.imwrite(target, YCrCb_result)
    except Exception as e:
        print(e)


def HSV(source, target):
    try:
        img = cv2.imread(source)

        # converting from gbr to hsv color space
        img_HSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # skin color range for hsv color space
        HSV_mask = cv2.inRange(img_HSV, (0, 15, 0), (17, 170, 255))
        HSV_mask = cv2.medianBlur(HSV_mask, 7)
        # 先开后闭
        HSV_mask = cv2.morphologyEx(
            HSV_mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        HSV_mask = cv2.morphologyEx(
            HSV_mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))

        HSV_result = cv2.bitwise_not(HSV_mask)
        # 抠图
        # global_result = cv2.bitwise_and(img, img, mask=global_mask)

        cv2.imwrite(target, HSV_result)
    except Exception as e:
        print(e)


def YCrCb_HSV(source, target):
    try:
        img = cv2.imread(source)

        # converting from gbr to hsv color space
        img_HSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # skin color range for hsv color space
        HSV_mask = cv2.inRange(img_HSV, (0, 15, 0), (17, 170, 255))
        HSV_mask = cv2.medianBlur(HSV_mask, 7)
        # 先开后闭
        HSV_mask = cv2.morphologyEx(
            HSV_mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        HSV_mask = cv2.morphologyEx(
            HSV_mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))

        # converting from gbr to YCbCr color space
        img_YCrCb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)

        # skin color range for hsv YCbCr space
        YCrCb_mask = cv2.inRange(img_YCrCb, (0, 135, 85), (255, 180, 135))
        # YCrCb_mask = cv2.inRange(img_YCrCb, (0, 0, 20), (234, 23, 10))
        YCrCb_mask = cv2.medianBlur(YCrCb_mask, 7)
        YCrCb_mask = cv2.morphologyEx(
            YCrCb_mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        YCrCb_mask = cv2.morphologyEx(
            YCrCb_mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))

        # merge skin detection (YCbCr and hsv)
        global_mask = cv2.bitwise_and(HSV_mask, YCrCb_mask)
        global_mask = cv2.medianBlur(global_mask, 11)
        global_mask = cv2.morphologyEx(
            global_mask, cv2.MORPH_OPEN, np.ones((4, 4), np.uint8))
        global_mask = cv2.morphologyEx(
            global_mask, cv2.MORPH_CLOSE, np.ones((4, 4), np.uint8))

        HSV_result = cv2.bitwise_not(HSV_mask)
        YCrCb_result = cv2.bitwise_not(YCrCb_mask)
        global_result = cv2.bitwise_not(global_mask)
        # 抠图
        # global_result = cv2.bitwise_and(img, img, mask=global_mask)

        cv2.imwrite(target, global_result)
    except Exception as e:
        print(e)


def deeplabv3(source, target):
    # def wrapper(source, target):
    model.eval()
    input_image = Image.open(source)
    input_image = input_image.convert("RGB")
    preprocess = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225]),
    ])
    input_tensor = preprocess(input_image)

    # create a mini-batch as expected by the model
    input_batch = input_tensor.unsqueeze(0)

    # move the input and model to GPU for speed if available
    input_batch = input_batch.to(device)

    # with torch.no_grad():
    output = model(input_batch)['out']
    output = output.squeeze()
    output_predictions = output.argmax(0)
    print(np.unique(output_predictions.detach().cpu().numpy()))
    # create a color pallette, selecting a color for each class
    palette = torch.tensor([2 ** 25 - 1, 2 ** 15 - 1, 2 ** 21 - 1])
    colors = torch.as_tensor([i for i in range(21)])[:, None] * palette
    colors = (colors % 255).numpy().astype("uint8")

    # plot the semantic segmentation predictions of 21 classes in each color
    r = Image.fromarray(output_predictions.byte().cpu().numpy()
                        ).resize(input_image.size)
    r.putpalette(colors)
    r = r.convert('RGB')
    cv2.imwrite(target, np.array(r))
    # plt.imshow(r)
    # plt.savefig(target)
    # return wrapper


def segment(source, target, method):
    if not os.path.exists(source):
        raise ValueError('source not exist')
    if not os.path.exists(target):
        os.mkdir(target)
    for classname in tqdm(os.listdir(source)):
        origin, dist = os.path.join(
            source, classname), os.path.join(target, classname)
        print(classname)
        if not os.path.exists(dist):
            os.mkdir(dist)
        if (not os.path.isdir(origin)) or (classname != 'bzx'):
            continue
        for filename in os.listdir(origin):
            if not filename.endswith('.jpg') and not filename.endswith('.jpeg') and not filename.endswith('.png'):
                continue

            method(os.path.join(origin, filename),
                   os.path.join(dist, filename))
            torch.cuda.empty_cache()
            print(f'processing {filename}')


if __name__ == '__main__':
    # model = torch.hub.load('pytorch/vision:v0.10.0',
    #                        'deeplabv3_resnet50', pretrained=True)
    # model.to(device)
    # torch.cuda.empty_cache()
    source = '/Users/jinyang/File/dataset'
    # target = '/home/djy/dataset/deeplabv3_dataset_aug'
    target = '/Users/jinyang/File/ycbcr_hsv_dataset'
    segment(source, target, YCrCb_HSV)
