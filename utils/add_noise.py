import cv2
import numpy as np

def add_noise(image, noise_type):
    if noise_type == 'gaussian':
        gauss_image = np.random.normal(0,np.random.randint(5,15),image.shape).astype(np.uint8)
        noise_image = image + gauss_image
        return noise_image
    if noise_type == 'saltpepper':
        noisy_image = image.copy()
        total_pixels = image.size // 3  # 每个像素由三个通道组成
        
        num_salt = int(total_pixels * 0.002)
        num_pepper = int(total_pixels * 0.002)
        
        # 添加盐噪声
        coords = [np.random.randint(0, i - 1, num_salt) for i in image.shape]
        noisy_image[coords[0], coords[1], :] = 255
        
        # 添加胡椒噪声
        coords = [np.random.randint(0, i - 1, num_pepper) for i in image.shape]
        noisy_image[coords[0], coords[1], :] = 0
        return noisy_image
    if noise_type == 'poisson':
        vals = len(np.unique(image))
        vals = 2 ** np.ceil(np.log2(vals))
        noisy = np.random.poisson(image * vals) / float(vals)
        noisy_image = np.clip(noisy, 0, 255).astype(np.uint8)
        return noisy_image
    if noise_type == 'uniform':
        uniform_noise = np.random.uniform(-50, 50, image.shape).astype(np.uint8)
        noisy_image = cv2.add(image, uniform_noise)
        return noisy_image
    if noise_type == 'None':
        return image