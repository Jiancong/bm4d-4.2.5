import numpy as np
from scipy.io import loadmat, savemat

SIZE=256

# 加载MAT文件
data = loadmat('10min_1155-23000-x-HAADF-Ti-wt.mat')

# 假设图像数据存储在名为'image_data'的键中
image_data = data['cls']

# 随机选择截取区域的起始点
start_x = np.random.randint(0, image_data.shape[0] - SIZE)
start_y = np.random.randint(0, image_data.shape[1] - SIZE)

print("start_x:", start_x)
print("start_y:", start_y)

# 截取512x512x3的区域
cropped_image = image_data[start_x:start_x+SIZE, start_y:start_y+SIZE, :]

# 将截取的区域保存到字典中
mat_data = {'crop': cropped_image}

# 保存字典到新的MAT文件
savemat('crop_image.mat', mat_data)
