
import argparse
import torch
import torch.backends.cudnn as cudnn
from torch.autograd import Variable
from PIL import Image
from torchvision.transforms import ToTensor
from os import listdir
from os.path import join, split, splitext
from scipy import misc

import scipy.io as scio
import numpy as np



def is_image_file(filename):
    return any(filename.endswith(extension) for extension in [".tif"])

def load_nor_img(filepath):
    img = misc.imread(filepath)
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
def PatchTest(model, GPU_IN_USE, image_crop, crop_shape):

    data1 = preprocessing(image_crop)



    # ===========================================================
    # model import & setting
    # ===========================================================

    if GPU_IN_USE:
        model.cuda()
        cudnn.benchmark = True
        # model = torch.load(args.model)

    num = data1.shape[3]

    out1 = np.zeros((num, 9))
    data1 = np.transpose(data1,axes=[3,1,2,0])
    data1 = np.transpose(data1,axes=[0,3,2,1])
    data1 = np.transpose(data1,axes=[0,2,1,3])
    print (data1.shape)
    num = 1
    temp1 = data1[0,:,:,:]
    print(temp1.shape)
    if GPU_IN_USE:
        # temp1 = Variable(ToTensor()(temp1)).view(1,-1,29,29)
        temp1 = Variable(torch.tensor(data1)).cuda()
    else :
        temp1 = Variable(torch.tensor(data1))
    print(temp1.shape)
    out = model(temp1)
    out = out.cpu()
    print(out.shape)
    print(out.data.numpy().shape)
    out1 = out.data.numpy()

 
    maxValue = np.max(out1, 1)
    maxIndex = np.zeros([out1.shape[0]]).astype(np.int32)
    for i in range(out1.shape[0]):
        temp = np.where(out1[i] == maxValue[i])
        temp = temp[0]
        temp = temp[0]
        maxIndex[i] = temp

    cnnClass = maxIndex.reshape(crop_shape)

    return cnnClass

#misc.imsave('./DATA/result/test2.tif', cnnClass)
#scio.savemat('./DATA/result/test.mat',{'pavia_spatial': out1})


