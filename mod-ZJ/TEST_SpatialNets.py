# -*- coding:utf-8 -*-
from __future__ import print_function
import argparse
import torch
import torch.backends.cudnn as cudnn
from torch.autograd import Variable
from PIL import Image
from torchvision.transforms import ToTensor
from os import listdir
from os.path import join, split, splitext

import os
import numpy as np
from TEST_Patch import PatchTest
from turn_label2rgb import turn_label2rgb
import tifffile
import cv2
import requests
import rasterio
from rasterio.transform import from_origin
from rasterio.crs import CRS
# ===========================================================
# Argument settings
# ===========================================================

def save_file(save_path, name, data, bound, dst_crs='epsg:3857'):
    """
    每次运行脚本时，将生成的数据存储到一个临时位置，通过commit方式，将这个文件夹上传入库
    按照给出的影像信息，将影像数据保存为本地文件
    :param name: str,  保存的文件名称
    :param data:     numpy.arr 影像数据 shape：(band, height, width)
    :param bound:    [w, s, e, n]
    :param dst_crs:  输出影像的坐标系
    :return: bool 创建成功，返回 True; 创建失败，返回 False.
    """

    isfolder(save_path)
    try:
        if len(data.shape) == 2:
            data = np.expand_dims(data, axis=0)
        height_res = abs(bound[3] - bound[1]) / data.shape[1]
        width_res = abs(bound[2] - bound[0]) / data.shape[2]
        transform = from_origin(bound[0], bound[3], height_res, width_res)
        with rasterio.open(save_path, 'w', driver='GTiff', height=data.shape[1], width=data.shape[2],
                            count=data.shape[0],
                            dtype=data.dtype, crs=CRS({'init': dst_crs}), transform=transform) as dst:
            dst.write(data)

    except Exception as err:
        print(err)
        return False
    else:
        return True

def is_image_file(filename):
    return any(filename.endswith(extension) for extension in [".png"])

def load_nor_img(filepath):
    img_4 = tifffile.imread(filepath)
    img = img_4[:,:,0:3] 
    # img = misc.imread(filepath)
    max_img = img.max()
    min_img = img.min()
    nor_img = (img - min_img) / (max_img - min_img)
    return nor_img

def preprocessing(data1):
    [r, w, b] = data1.shape
    w_size = 29
    data1_pad = np.pad(data1, ((14, 14), (14, 14), (0, 0)), 'symmetric')
    PatchImage = np.zeros([w_size, w_size, b, r*w])
    mark =0
    for i in range(r):
        for j in range(w):
            PatchImage[:, :, :, mark] = data1_pad[i: i + w_size, j: j + w_size, :]
            mark = mark + 1

    return PatchImage

def thumbnail_size_keep_ratio(rows, cols, max_size = 1300):
    ratio = max(float(rows)/float(max_size), float(cols)/float(max_size))
    thumb_rows = int(rows/ratio)
    thumb_cols = int(cols/ratio)
    print(thumb_rows, thumb_cols)
    return thumb_rows, thumb_cols

def isfolder( filepath ):

    save_file_path_list = filepath.split('/')

    if filepath[0] == '/' :
        save_file_path = '/'  + save_file_path_list[0]
    else:
        save_file_path = save_file_path_list[0]
    
    for idx in range(1,len(save_file_path_list)-1):
        save_file_path = os.path.join(save_file_path,save_file_path_list[idx])
        if not os.path.exists(save_file_path):
            os.mkdir(save_file_path)
    print(save_file_path)

    return

def conver_images(file_name, model_path, save_file_name, save_thumbnail_file_name = 'thumb.tif', img_uid = 0, uid = 0, ip_port=''):
    os.environ['CUDA_VISIBLE_DEVICES'] = '0'
    GPU_IN_USE = torch.cuda.is_available()
    
    model = torch.load(model_path, map_location=lambda storage, loc: storage)

    split_num = 231
    patchCNN = np.zeros([])
    x = file_name
    image = load_nor_img(x)
    cropsize_r = 30
    row = image.shape[0]
    col = image.shape[1]

    split_num = int (float(row)/float(cropsize_r) + 1.0)
    patchCNN = np.zeros([row, col]).astype(np.int32)
    for i in range(split_num):
        print('image name: ',x ,'\n  strides -  ', i)
        if i+1 == split_num:
            image_crop = image[i* cropsize_r: row, :, :]
            patchCNN[i* cropsize_r: row, :] = PatchTest(model, GPU_IN_USE, image_crop, [image_crop.shape[0], col])
        else:
            image_crop = image[i* cropsize_r: (i+1)*cropsize_r, :, :]
            patchCNN[i* cropsize_r: (i+1)*cropsize_r, :] = PatchTest(model, GPU_IN_USE, image_crop, [image_crop.shape[0], col])

    rgb_result = turn_label2rgb(patchCNN)
    thumb_rows, thumb_cols = thumbnail_size_keep_ratio(row,col)
    rgb_thumbnail = cv2.resize(rgb_result,(thumb_rows, thumb_cols))

    isfolder(save_file_name)
    isfolder(save_thumbnail_file_name)

    tifffile.imsave(save_file_name,rgb_result)
    tifffile.imsave(save_thumbnail_file_name,rgb_thumbnail)

    json_list = {}
    json_list['uid'] = uid
    json_list['app_images_uid'] = img_uid

    url = "http://" + ip_port+ "/model_app/saveDetAppResultFromGPU"
    r = requests.post(url, json=json_list)
    print('post -- ', str(url))

    return


if __name__=='__main__':
    # row = 6908
    # cropsize_r = 60
    # split_num = int (float(row)/float(cropsize_r) + 1.0)
    # print(split_num)
    conver_images(file_name = '/storage/geocloud/test/data/原始影像数据库/GF2/L1A/PMS/4m多光谱/GF2_PMS1_E112.9_N23.3_20170831_L1A0002574623-MSS1.tiff',model_path='/root/workdir/python/DATA/train/SpatialNets_model_path.pth', save_file_name = '/storage/tmp/result.tif',save_thumbnail_file_name = '/storage/tmp/thumbnail.tif')
    # thumbnail_size_keep_ratio(6908,7300)


