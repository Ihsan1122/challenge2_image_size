import pandas as pd
import numpy as np
import cv2

def apply_custom_colormap(image):
    colormap = cv2.COLORMAP_JET
    colored_image = cv2.applyColorMap(image, colormap)
    return colored_image

def resize_image(image):
    resized_image = cv2.resize(image, (150, 1), interpolation=cv2.INTER_AREA)
    return resized_image

def load_and_resize(csv_path):
    df = pd.read_csv(csv_path)

    processed_images = []

    for index, row in df.iterrows():
        if row.isnull().any():
            continue  # Skip rows with NaN values

        image = np.array(row[1:], dtype=np.uint8).reshape(1, -1)  # Assuming columns col1 to col200 are pixel values
        resized_image = resize_image(image)
        colored_image = apply_custom_colormap(resized_image)
        processed_images.append({'depth': int(row['depth']), 'pixels': colored_image.flatten()})

    return processed_images

# Example usage if executed as standalone script
if __name__ == '__main__':
    csv_path = 'data.csv'  # Replace with your CSV file path
    processed_images = load_and_resize(csv_path)
    print(processed_images)
