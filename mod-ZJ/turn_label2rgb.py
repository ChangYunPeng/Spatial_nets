from PIL import Image
import numpy as np
from scipy.io import loadmat
import random
import os
import time
import tifffile
import cv2
import shutil
COLOR_MAP = [[0, 0, 255], [0, 255, 0], [0, 255, 255], [255, 0, 0], [255, 255, 0]]

P_COLOR_MAP = [190, 40, 220, 15, 45]


def turn_png2label(arr):
    label_class = np.zeros(shape=(arr.shape[0]*arr.shape[1]))
    # arr = arr.flatten()
    for idx in range(len(P_COLOR_MAP)):
        label_class = np.where(arr.flatten()==P_COLOR_MAP[idx], idx+1, label_class)
        # print label_class.shape
    label_class = np.reshape(label_class, newshape=(arr.shape[0], arr.shape[1], 1))
    return label_class

def turn_label2png(arr):
    label_class = np.zeros(shape=(arr.shape[0]*arr.shape[1]))
    # arr = arr.flatten()
    for idx in range(len(P_COLOR_MAP)):
        label_class = np.where(arr.flatten()==idx , P_COLOR_MAP[idx], label_class)
        # print label_class.shape
    label_class = np.reshape(label_class, newshape=(arr.shape[0], arr.shape[1], 1))
    return label_class

def turn_rgb2label(arr):
    label_class = np.zeros(shape=(arr.shape[0], arr.shape[1]))

    for idx in range(len(COLOR_MAP)):
        label_class = np.where((arr == COLOR_MAP[idx]).all(), idx+1, label_class)
    # print arr
    return label_class


def turn_label2rgb(arr):
    # print arr.max()
    r_arr = np.ones(shape=(arr.shape[0] * arr.shape[1]))
    g_arr = np.ones(shape=(arr.shape[0] * arr.shape[1]))
    b_arr = np.ones(shape=(arr.shape[0] * arr.shape[1]))

    for idx in range(len(COLOR_MAP)):
        r_arr = np.where(arr.flatten() == idx , COLOR_MAP[idx][0], r_arr)
        g_arr = np.where(arr.flatten() == idx , COLOR_MAP[idx][1], g_arr)
        b_arr = np.where(arr.flatten() == idx , COLOR_MAP[idx][2], b_arr)
    # print r_arr.shape
    r_arr = np.reshape(r_arr, newshape=(arr.shape[0], arr.shape[1], 1))
    g_arr = np.reshape(g_arr, newshape=(arr.shape[0], arr.shape[1], 1))
    b_arr = np.reshape(b_arr, newshape=(arr.shape[0], arr.shape[1], 1))
    rgb_arr = np.concatenate([ b_arr, g_arr, r_arr], axis=2)
    rgb_arr = rgb_arr.astype(np.uint8)
    return rgb_arr

def turn_mat_2_tif(mat_path, save_path):
    mat_path = '/Users/changyunpeng/CODE/DATA/GF2_PMS2_E113.4_N23.1_20171208_L1A0002831089-MSS2.mat'
    cl_mat = loadmat(mat_path)  
    cl_mat = cl_mat['pavia_spatial']
    print (cl_mat.max())
    print(cl_mat.min())
    print(cl_mat.shape)
    rgb_mat = turn_label2rgb(cl_mat)
    print(rgb_mat.shape)
    cv2.imwrite('./GF2_PMS2_E113.4_N23.1_20171208_L1A0002831089-MSS2.jpg', rgb_mat)
    return

if __name__=='__main__':
    mat_folder_path = '/home/room304/storage/mod-ZJ/DATA/result'
    folder_list = os.listdir(mat_folder_path)
    xml_folder_path = '/home/room304/storage/unzip-GF2'
    target_foldere_path = '/home/room304/storage/classed_GF2'
    mat_path_list = os.listdir(mat_folder_path)
    for i,mat_path_iter in enumerate(mat_path_list):

        if mat_path_iter[-4:] == '.mat':
            unzip_floder_path = os.path.join(xml_folder_path, mat_path_iter[:-9] + '.')
            xml_path = os.path.join(unzip_floder_path,mat_path_iter[:-4]+'.xml')
            mat_path = os.path.join(mat_folder_path, mat_path_iter)
            if os.path.isfile(xml_path):
                print('%d',i)
                print('mat path', mat_path)
                print('xml path', xml_path)
                target_path_iter = os.path.join(target_foldere_path, mat_path_iter[:-9])
                if not os.path.exists(target_path_iter):
                    os.mkdir(target_path_iter)
                print('target path', target_path_iter)
                shutil.move(xml_path,target_path_iter)
                shutil.move(mat_path_iter,target_path_iter)

            


