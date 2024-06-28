import matplotlib.pyplot as plt
import numpy as np

def apply_custom_colormap(image):
    image = image.reshape(1, 150)  # Ensure the image is 2D
    colormap = plt.get_cmap('viridis')  # Use the 'viridis' colormap
    colored_image = colormap(image / 255.0)  # Normalize and apply colormap
    return (colored_image[:, :, :3] * 255).astype(np.uint8)  # Drop alpha channel and convert to uint8

