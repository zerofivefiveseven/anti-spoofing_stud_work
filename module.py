import json
import cv2
import os
import time
import sys

import logging

import numpy as np

# ================================================================================
# Please change following path to your OWN
LOCAL_ROOT = './'
LOCAL_IMAGE_LIST_PATH = 'data/CelebA_Spoof/metas/intra_test/test_label.json'


# ================================================================================


def read_image(image_path):
    """
    Read an image from input path

    params:
        - image_local_path (str): the path of image.
    return:
        - image: Required image.
    """

    image_path = LOCAL_ROOT + image_path

    img = cv2.imread(image_path)
    # Get the shape of input image
    real_h, real_w, c = img.shape
    assert os.path.exists(image_path[:-4] + '_BB.txt'), 'path not exists' + ' ' + image_path

    with open(image_path[:-4] + '_BB.txt', 'r') as f:
        material = f.readline()
        try:
            x, y, w, h, score = material.strip().split(' ')
        except:
            logging.info('Bounding Box of' + ' ' + image_path + ' ' + 'is wrong')

        try:
            w = int(float(w))
            h = int(float(h))
            x = int(float(x))
            y = int(float(y))
            w = int(w * (real_w / 224))
            h = int(h * (real_h / 224))
            x = int(x * (real_w / 224))
            y = int(y * (real_h / 224))

            # Crop face based on its bounding box
            y1 = 0 if y < 0 else y
            x1 = 0 if x < 0 else x
            y2 = real_h if y1 + h > real_h else y + h
            x2 = real_w if x1 + w > real_w else x + w
            img = img[y1:y2, x1:x2, :]

        except:
            logging.info('Cropping Bounding Box of' + ' ' + image_path + ' ' + 'goes wrong')

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img


def get_image(max_number=None):
    """
    This function returns a iterator of image.
    It is used for local test of participating algorithms.
    Each iteration provides a tuple of (image_id, image), each image will be in RGB color format with array shape of (height, width, 3)

    return: tuple(image_id: str, image: numpy.array)
    """
    with open(LOCAL_ROOT + LOCAL_IMAGE_LIST_PATH) as f:
        image_list = json.load(f)
    logging.info("got local image list, {} image".format(len(image_list.keys())))
    Batch_size = 1024
    logging.info("Batch_size=, {}".format(Batch_size))
    n = 0
    final_image = []
    final_image_id = []
    for idx, image_id in enumerate(image_list):
        # get image from local file
        try:
            image = read_image(image_id)
            final_image.append(image)
            final_image_id.append(image_id)
            n += 1
        except:
            logging.info("Failed to read image: {}".format(image_id))
            raise

        if n == Batch_size or idx == len(image_list) - 1:
            np_final_image_id = np.array(final_image_id)
            np_final_image = np.array(final_image)
            n = 0
            final_image = []
            final_image_id = []
            yield np_final_image_id, np_final_image

celebA_spoof_image_iter = get_image()
