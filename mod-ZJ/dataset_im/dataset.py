import torch.utils.data as data

from os import listdir
from os.path import join
from scipy import misc

from PIL import Image
from scipy import misc

import numpy as np
import random
import scipy.io as scio

from os import listdir
from os.path import join

from torch.utils.data import Dataset
from torchvision.transforms import ToTensor

def is_image_file(filename):
    return any(filename.endswith(extension) for extension in [".tif"])


def load_nor_img(filepath):
    img = misc.imread(filepath)
    max_img = img.max()
    min_img = img.min()
    nor_img = (img - min_img) / (max_img - min_img)
    return nor_img

def load_label(filepath):
    label = misc.imread(filepath)
    return label


def preprocessing(data1, data2):
    [r, w, b] = data1.shape

    w_size = 29

    data1_pad = np.pad(data1, ((14, 14), (14, 14), (0, 0)), 'symmetric')

    label_r = data2[:, :, 0]
    label_g = data2[:, :, 1]
    label_b = data2[:, :, 2]
    label_value = np.array([[0, 0, 255], [0, 255, 0], [0, 255, 255], [255, 0, 0], [255, 255, 0]])
    label_num = label_value.shape[0]
    Sample_num = np.zeros([label_num, 1]).astype(np.int32)
    ground_truth = np.zeros([r, w]).astype(np.int32)

    Sample_index = np.empty((label_num, 1), dtype = object)
    for i in range(label_num):
        ind_r = (label_r == label_value[i, 0])
        ind_g = (label_g == label_value[i, 1])
        ind_b = (label_b == label_value[i, 2])
        ind = (ind_r & ind_g & ind_b)
        [row, col] = np.where(ind == 1)
        ground_truth[row, col] = i + 1
        num_C = len(row)
        Sample_num[i] = round(0.001*num_C)
        index = list(zip(row, col))
        random.shuffle(index)
        Sample_index[i, 0] = index

#    scio.savemat('ground_truth.mat', {'ground_truth': ground_truth})

    SumSampleNum = sum(Sample_num)
#    a = SumSampleNum[0]
    PatchImage = np.zeros([w_size, w_size, b, SumSampleNum[0]])
    PatchLabel = np.zeros([1, SumSampleNum[0]]).astype(np.int32)

    mark =0
    for i in range(label_num):
        for j in range(Sample_num[i, 0]):
            temp = Sample_index[i]
            temp = temp[0]
            [r_ind, c_ind] = temp[j]
            PatchImage[:, :, :, mark] = data1_pad[r_ind: r_ind + w_size, c_ind: c_ind + w_size, :]
            PatchLabel[:, mark] = ground_truth[r_ind, c_ind]
            mark = mark + 1

    return PatchImage, PatchLabel

class DatasetFromFolder(data.Dataset):
    def __init__(self, data_dir, label_dir):
        super(DatasetFromFolder, self).__init__()
        image_filenames = [join(data_dir, x) for x in listdir(data_dir) if is_image_file(x)]
        label_filenames = [join(label_dir, y) for y in listdir(label_dir) if is_image_file(y)]

        image_list = []
        label_list = []
        #num1 = data1.shape[3]

        for (x1, x2, y1, y2) in zip(image_filenames, listdir(data_dir), label_filenames, listdir(label_dir)):
            temp = y2[:-10] + '.tif'
            if x2 == temp:
                data1 = load_nor_img(x1)
                data2 = load_label(y1)
                [PatchImage, PatchLabel] = preprocessing(data1, data2)
                count = PatchImage.shape[3]
                for i in range(count):
                    temp1 = PatchImage[:, :, :, i]
                    temp2 = PatchLabel[:, i]
                    temp11 = ToTensor()(temp1)
                    image_list.append(temp11)
                    label_list.append(temp2)

            else:
                print("Error: imagename does not math with labelname!")
        self.image = image_list
        self.label = label_list


    def __getitem__(self, index):

        return self.image[index], self.label[index]

    def __len__(self):
        return len(self.label)
