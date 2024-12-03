import numpy as np
from bm4d import bm4d
from scipy.io import loadmat, savemat
import matplotlib.pyplot as plt
from experiment_funcs import get_psnr, official_get_psnr, calculate_ms_ssim


def denoise_image(noisy_image, psd):
    # 使用BM4D算法去噪
    denoised_image = bm4d(noisy_image, psd).astype(np.uint8)
    print("denoised_image shape:", denoised_image.shape)
    
    # 计算并打印PSNR
    psnr_value = get_psnr(denoised_image, noisy_image)
    print("PSNR: ", psnr_value)

    o_psnr_value = official_get_psnr(denoised_image, noisy_image)
    print("O-PSNR:", o_psnr_value)


    # 计算并打印SSIM
    ssim= calculate_ms_ssim(denoised_image, noisy_image)
    print("SSIM:", ssim)
    
    return denoised_image

# 加载含噪声的原始图像（这里假设你已经有了一个含噪声的图像数组）
#noisy_image = loadmat('1min_1210_Ti+Cr.mat')['cls']
#noisy_image = loadmat('crop_image.mat')['crop']
noisy_image = loadmat('EDSLayeredImage1.mat')['cls']

# 如果你知道噪声的PSD，直接使用它
# 如果你不知道PSD，你可能需要先估计它，或者使用一些默认值

psd = 0.0008 * np.max(noisy_image) ** 2 # 这里假设我们没有PSD信息
print("psd:", psd)

# 调用去噪函数
denoised_image = denoise_image(noisy_image, psd)

print("denoised_image shape:", denoised_image.shape)

# 显示或保存去噪后的图像
plt.imshow(denoised_image)
plt.show()

mat_data = {'dimage': denoised_image}
savemat('dimage.mat', mat_data)
