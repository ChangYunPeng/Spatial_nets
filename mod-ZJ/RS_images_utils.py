
from PIL import Image
import numpy as np
import tifffile


def block_tiff_imgs(img_path, stander_size=1024,c_r = 3, c_g = 2, c_b = 1):
    # im_path = '/Users/changyunpeng/CODE/python/GF2_PMS2_E105.5_N25.8_20171224_L1A0002875623/GF2_PMS2_E105.5_N25.8_20171224_L1A0002875623-PAN2.tiff'
    # imname = 'GF2_PMS1_E113.5_N23.0_20151219_L1A0001293546-MSS1.tif'
    iomat = tifffile.imread(img_path)
    print (iomat.dtype)
    print (iomat.shape)
    u8_mat = turn_mat_uint16_uint8(iomat,c_r,c_g,c_b)
    # u8_mat = iomat.astype(np.uint8)
    block_mat_list, block_mat_init_location = block_rgb_mat(u8_mat,stander_size,stander_size)
    return block_mat_list, block_mat_init_location, iomat.shape[0], iomat.shape[1]

def block_png_imgs(img_path, stander_size):
    im_path = '/Users/changyunpeng/CODE/python/GF2_PMS2_E105.5_N25.8_20171224_L1A0002875623/GF2_PMS2_E105.5_N25.8_20171224_L1A0002875623-PAN2.tiff'
    im = Image.open(img_path)
    u8_mat = np.mat(im,dtype=np.uint8)
    block_mat_list, block_mat_init_location = block_rgb_mat(u8_mat, stander_size, stander_size)
    return block_mat_list, block_mat_init_location

def block_rgb_mat(u8_mat,stander_block_w = 1024,stander_block_h = 1024 ):
    print (u8_mat.shape)
    block_w_s_neg = np.int(np.float(u8_mat.shape[0]) / np.float(stander_block_w))
    block_h_s_neg = np.int(np.float(u8_mat.shape[1]) / np.float(stander_block_h))
    block_w_s_pos = block_w_s_neg + 1
    block_h_s_pos = block_h_s_neg + 1

    block_w_neg = np.float(u8_mat.shape[0]) / np.float(block_w_s_neg)
    block_h_neg = np.float(u8_mat.shape[1]) / np.float(block_h_s_neg)
    block_w_pos = np.float(u8_mat.shape[0]) / np.float(block_w_s_pos)
    block_h_pos = np.float(u8_mat.shape[1]) / np.float(block_h_s_pos)

    print (block_w_neg, block_h_neg)
    print (block_w_pos, block_h_pos)

    if (block_w_neg - stander_block_w) > (stander_block_w - block_w_pos):
        block_w = block_w_pos
        block_w_s = block_w_s_pos
    else:
        block_w = block_w_neg
        block_w_s = block_w_s_neg

    if (block_h_neg - stander_block_h) > (stander_block_h - block_h_pos):
        block_h = block_h_pos
        block_h_s = block_h_s_pos
    else:
        block_h = block_h_neg
        block_h_s = block_h_s_neg

    print (block_w, block_h)
    print (block_w_s, block_h_s)
    block_w = np.int(block_w)
    block_h = np.int(block_h)
    block_w_s = np.int(block_w_s)
    block_h_s = np.int(block_h_s)

    block_mat_list = []
    block_mat_init_location = []
    print (block_w_s * block_w, block_h_s * block_h)

    for w_idx in range(block_w_s):
        for h_idx in range(block_h_s):
            print (w_idx, h_idx)
            init_local = {}
            init_local['W'] = h_idx * block_h
            init_local['H'] = w_idx * block_w 

            init_local['H_idx'] = w_idx
            init_local['W_idx'] = h_idx

            init_local['H_lt'] = w_idx * block_w
            init_local['W_lt'] = h_idx * block_h

            if (w_idx + 1) == block_w_s:
                init_local['H_rd'] = u8_mat.shape[0]
            else:
                init_local['H_rd'] = (w_idx+1) * block_w

            if (h_idx + 1) == block_w_s:
                init_local['W_rd'] = u8_mat.shape[1]
            else:
                init_local['W_rd'] = (h_idx+1) * block_h

            print (init_local)
            block_mat_init_location.append(init_local)
            block_mat_list.append(
                u8_mat[init_local['H_lt']: init_local['H_rd'], init_local['W_lt']: init_local['W_rd'], :])

    return block_mat_list, block_mat_init_location

def hist_2_98(input_mat):
    if len(input_mat) == 3:
        img = input_mat[:,:,0]
    else:
        img = input_mat
    p2, p98 = np.percentile(img, (2, 98))

    img = np.where(img > p2, img, p2)
    img = np.where(img < p98, img, p98)
    img = (img - p2) / (p98 - p2) * 255.0
    img = img.astype(np.uint8)
    #print p2,p98
    img = img[:,:,np.newaxis]
    return img

def hist_rgb_2_98(rgb_mat):
    img = rgb_mat
    p2, p98 = np.percentile(img, (2, 98))

    img = np.where(img > p2, img, p2)
    img = np.where(img < p98, img, p98)
    img = (img - p2) / (p98 - p2) * 255.0
    img = img.astype(np.uint8)
    #print p2,p98
    # img = img[:,:,np.newaxis]
    return img

def turn_mat_uint16_uint8(uint16_iomat,c_r = 0, c_g = 1, c_b = 2):
    """
    :param uint16_iomat: uint16 np.mat
    :return: uint8 mat
    """
    float_iomat = uint16_iomat.astype(np.float)
    float_r_mat = hist_2_98(float_iomat[:,:,c_r])
    float_g_mat = hist_2_98(float_iomat[:,:,c_g])
    float_b_mat = hist_2_98(float_iomat[:,:,c_b])
    float_mat = np.concatenate([float_r_mat,float_g_mat,float_b_mat],axis=2)
    u8_mat = float_mat.astype(np.uint8)
    return u8_mat

def save_tiff_png(tiff_path,png_path):
    """
    :param tiff_path: multi channel RS images, uint16,  tiff , path
    :param png_path: RGB channel RS images, uint8  png , path
    :return: save uint16 tiff file as uint8 png file
    """
    iomat = tifffile.imread(tiff_path)
    outmat = turn_mat_uint16_uint8(iomat)
    img_save = Image.fromarray(outmat, mode='RGB')
    img_save.save(png_path)
    return

if __name__=='__main__':
    im_path = '/Users/changyunpeng/CODE/python/GF2_PMS2_E105.5_N25.8_20171224_L1A0002875623/GF2_PMS2_E105.5_N25.8_20171224_L1A0002875623-MSS2.tiff'
    block_tiff_imgs(im_path,stander_size=512)
