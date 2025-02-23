"""
Define functions needed for the demos.
"""

import numpy as np
from scipy.fftpack import fftn, ifftn, fft2, ifft2, fftshift, ifftshift
from scipy.signal import fftconvolve
from bm4d import gaussian_kernel_3d, gaussian_kernel
from skimage.metrics import peak_signal_noise_ratio as compare_psnr
from pytorch_msssim import ssim, ms_ssim
import torch


# 范围为0-1，越大越相似。一般在0.9以上就认为相似度较高
def calculate_ms_ssim(img1, img2):
    img1_tensor = torch.from_numpy(img1).permute(2, 0, 1).unsqueeze(0).float()
    img2_tensor = torch.from_numpy(img2).permute(2, 0, 1).unsqueeze(0).float()
    ms_ssim_value = ms_ssim(img1_tensor, img2_tensor, data_range=255, size_average=False)
    return ms_ssim_value[0].numpy().item()

def official_get_psnr(y_est: np.ndarray, y_ref: np.ndarray) -> float:
    psnr_value = compare_psnr(y_est, y_ref, data_range=255)
    return psnr_value


def get_psnr(y_est: np.ndarray, y_ref: np.ndarray) -> float:
    """
    Return PSNR value for y_est and y_ref presuming the noise-free maximum is 1.
    :param y_est: Estimate array
    :param y_ref: Noise-free reference
    :return: PSNR value
    """
    return 10 * np.log10(np.abs(np.max(y_ref))**2 / np.mean(np.abs((y_est - y_ref).ravel()) ** 2))


def get_cropped_psnr_3d(y_est: np.ndarray, y_ref: np.ndarray, crop: tuple) -> float:
    """
    Return PSNR value for y_est and y_ref presuming the noise-free maximum is 1.
    Crop the images before calculating the value by crop.
    :param y_est: Estimate array
    :param y_ref: Noise-free reference
    :param crop: Tuple of crop-x and crop-y from both stides
    :return: PSNR value
    """
    return get_psnr(np.atleast_3d(y_est)[crop[0]:-crop[0], crop[1]:-crop[1], crop[2]:-crop[2]],
                    np.atleast_3d(y_ref)[crop[0]:-crop[0], crop[1]:-crop[1], crop[2]:-crop[2]])


def get_experiment_kernel(noise_type: str, noise_var: float, sz: tuple = np.array((101, 101))):
    """
    Get kernel for generating noise from specific experiment from the paper.
    :param noise_type: Noise type string, g[0-4](w|)
    :param noise_var: noise variance
    :param sz: size of image, used only for g4 and g4w
    :return: experiment kernel with the l2-norm equal to variance
    """
    # if noiseType == gw / g0
    kernel = np.array([[1]])
    noise_types = ['gw', 'g0', 'g1', 'g2', 'g3', 'g4', 'g1w', 'g2w', 'g3w', 'g4w']
    if noise_type not in noise_types:
        raise ValueError("Noise type must be one of " + str(noise_types))

    if noise_type != "g4" and noise_type != "g4w":
        # Crop this size of kernel when generating,
        # unless pink noise, in which
        # if noiseType == we want to use the full image size
        sz = np.array([71, 71])
    else:
        sz = np.array(sz)

    # Sizes for meshgrids
    sz2 = -(1 - (sz % 2)) * 1 + np.floor(sz / 2)
    sz1 = np.floor(sz / 2)
    uu, vv = np.meshgrid([i for i in range(-int(sz1[0]), int(sz2[0]) + 1)],
                         [i for i in range(-int(sz1[1]), int(sz2[1]) + 1)])

    beta = 0.8

    if noise_type[0:2] == 'g1':
        # Horizontal line
        kernel = np.atleast_2d(16 - abs(np.linspace(1, 31, 31) - 16))

    elif noise_type[0:2] == 'g2':
        # Circular repeating pattern
        scale = 1
        dist = uu ** 2 + vv ** 2
        kernel = np.cos(np.sqrt(dist) / scale) * gaussian_kernel((sz[0], sz[1]), 10)

    elif noise_type[0:2] == 'g3':
        # Diagonal line pattern kernel
        scale = 1
        kernel = np.cos((uu + vv) / scale) * gaussian_kernel((sz[0], sz[1]), 10)

    elif noise_type[0:2] == 'g4':
        # Pink noise
        dist = uu ** 2 + vv ** 2
        n = sz[0] * sz[1]
        spec = (np.sqrt((np.sqrt(n) * 1e-2) / (np.sqrt(dist) + np.sqrt(n) * 1e-2)))
        kernel = fftshift(ifft2(ifftshift(spec)))

    else:  # gw and g0 are white
        beta = 0

    # -- Noise with additional white component --

    if len(noise_type) > 2 and noise_type[2] == 'w':
        kernel = kernel / np.sqrt(np.sum(kernel ** 2))
        kalpha = np.sqrt((1 - beta) + beta * abs(fft2(kernel, (sz[0], sz[1]))) ** 2)
        kernel = fftshift(ifft2(kalpha))

    kernel = np.real(kernel)
    # Correct variance
    kernel = kernel / np.sqrt(np.sum(kernel ** 2)) * np.sqrt(noise_var)

    return kernel


def generate_noise(kernel: np.ndarray, realization: int, sz: tuple)\
        -> (np.ndarray, np.ndarray, np.ndarray):
    """
    Generate noise for experiment with specified kernel, variance, seed and size.
    Return noise and relevant parameters.
    The generated noise is non-circular.
    :param kernel: Noise kernel, not scaled
    :param realization: Seed for the noise realization
    :param sz: image size -> size of resulting noise
    :return: noise, PSD, and kernel
    """
    np.random.seed(realization)
    kernel = np.atleast_3d(kernel)

    # Create noisy image
    half_kernel = np.ceil(np.array(kernel.shape) / 2)
    half_kernel = np.array(half_kernel, dtype=int)

    # Crop edges
    noise = fftconvolve(np.random.normal(size=(sz + 2 * half_kernel)), kernel, mode='same')
    noise = np.atleast_3d(noise)[half_kernel[0]:-half_kernel[0],
                                 half_kernel[1]:-half_kernel[1],
                                 half_kernel[2]:-half_kernel[2]]

    psd = abs(fftn(kernel, sz)) ** 2 * sz[0] * sz[1] * sz[2]

    return noise, psd, kernel
