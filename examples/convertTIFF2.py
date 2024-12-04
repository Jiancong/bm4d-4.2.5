import cv2
import numpy as np
from scipy.io import savemat
import argparse


parser = argparse.ArgumentParser(description='This is a demo programe for converting file format')

parser.add_argument('input', help='input tif file path')

# 读取图像
#img = cv2.imread('/home/jiancong/Sources/北理工/暴老师/Bao/10min_1155-23000-x-HAADF-Mo-wt.tif', cv2.IMREAD_UNCHANGED)
#img = cv2.imread('1210_Ti+Cr.tif', cv2.IMREAD_UNCHANGED)
#img = cv2.imread('resize.tif', cv2.IMREAD_UNCHANGED)

args = parser.parse_args()
#img = cv2.imread('EDSLayeredImage1.tiff2.tiff', cv2.IMREAD_UNCHANGED)
img = cv2.imread(args.input, cv2.IMREAD_UNCHANGED)

# 检查是否为4通道图像
if img.shape[2] == 4:
    # 转换为3通道图像
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    # 选红色
    #img_single_channel = np.array(img[:, :, 0])
    #savemat('10min_1155-23000-x-HAADF-Ti-wt.mat', {'single': img_single_channel})

# 将图像数据转换为numpy数组
img_array = img.reshape((img.shape[0], img.shape[1], 3))

# 保存为.mat文件
#savemat('10min_1155-23000-x-HAADF-Mo-wt.mat', {'cls': img_array})
#savemat('1min_1210_Ti+Cr.mat', {'cls': img_array})

savefile_name=args.input[:-4] + ".mat"

savemat(savefile_name, {'cls': img_array})


# 保存3通道图像
#cv2.imwrite('10min_1155-23000-x-HAADF-Cr-wt-3channels.tif', img)
