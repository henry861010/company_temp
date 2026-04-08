import numpy as np
from PIL import Image
import itertools
import os

def generate_all_images(length, width, dir=None):
    # All possible values for a single pixel
    pixel_values = [0, 255]
    num_pixels = length * width
    all_combinations = itertools.product(pixel_values, repeat=num_pixels)
    
    if len(all_combinations) < 1000:
        if dir is not None and not os.path.exists(dir):
            os.makedirs(dir)
        

        
        imgs = []
        for i, combo in enumerate(all_combinations):
            # Convert the tuple to a numpy array and reshape to length x width
            array = np.array(combo, dtype=np.uint8).reshape((width, length))
            
            # Create and save image
            img = Image.fromarray(array, mode='L')
            imgs.append(img)
            
            if dir is not None:
                img.save(f"{dir}/{i}.png")
        return imgs
    else:
        return []

def generate_image(length, width, dir=None):
    if dir is not None and not os.path.exists(dir):
        os.makedirs(dir)
        
    # Generate a random array of 0s and 1s
    # Then multiply by 255 to get black (0) and white (255)
    random_grid = np.random.choice([0, 255], size=(width, length), p=[0.5, 0.5])
    
    # Convert the numpy array to an unsigned 8-bit integer type
    array_uint8 = random_grid.astype(np.uint8)
    
    # Create an image from the array ('L' mode is for grayscale)
    img = Image.fromarray(array_uint8, mode='L')
    
    if dir is not None:
        img.save(f"{dir}/1.png")
    
    return img

# Example usage: 500x500 image
img = generate_image(10, 10)
#img.save("/Users/henry/Desktop/company_temp/cdf_solver/data/img.png")

# Warning: Only run this for very small values like 2x2 or 3x3
imgs = generate_all_images(3, 3, dir="/Users/henry/Desktop/company_temp/cdf_solver/data/data")