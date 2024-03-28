# mainCrop.py

import os

import matplotlib.pyplot as plt
from PIL import Image
import cv2
import numpy as np

def create_crops(img, crop_size=(224, 224)):
    img_width, img_height = img.size

    crops = []
    for start_x in range(0, img_width, crop_size[0]):
        if start_x + crop_size[0] > img_width:
            start_x = img_width - crop_size[0]
        for start_y in range(0, img_height, crop_size[1]):
            if start_y + crop_size[1] > img_height:
                start_y = img_height- crop_size[1]
                # break

            imgCrop = img.crop((start_x, start_y, start_x + crop_size[0], start_y + crop_size[1]))

            crops.append(imgCrop)
    return crops

def reconstruct_image(crops, original_size):
    """
    Reconstructs the original image from a list of non-overlapping crops.

    Args:
        crops (list): A list of PIL Image objects representing the crops.
        original_size (tuple): A tuple (width, height) representing the size
            of the original image.

    Returns:
        PIL.Image: The reconstructed original image.

    Raises:
        ValueError: If the number of crops doesn't match the expected number
            based on the original size and crop size used in `create_crops`.
    """

    crop_width, crop_height = crops[0].size  # Assuming all crops have the same size

    # Calculate the expected number of crops based on original size and crop size
    expected_num_crops_x = int(original_size[0] / crop_width) + (
        1 if original_size[0] % crop_width != 0 else 0
    )
    expected_num_crops_y = int(original_size[1] / crop_height) + (
        1 if original_size[1] % crop_height != 0 else 0
    )
    expected_total_crops = expected_num_crops_x * expected_num_crops_y

    if len(crops) != expected_total_crops:
        raise ValueError(
            "Number of crops ({}) doesn't match expected number ({}) based on original size and crop size used in create_crops.".format(
                len(crops), expected_total_crops
            )
        )

    # Create a new image with the original size and the same mode as the crops
    reconstructed_img = Image.new(crops[0].mode, original_size)
    paste_x, paste_y = 0, 0

    for i, crop in enumerate(crops):
        reconstructed_img.paste(crop, (paste_x, paste_y))

        # Update paste coordinates for the next crop
        paste_y += crop_height

        if paste_y == original_size[1]:
            # cv2.imshow("reconstructed_img",np.array(reconstructed_img))
            # cv2.waitKey()
            paste_y = 0
            paste_x += crop_width
            if paste_x > original_size[0] - crop_width:
                paste_x = original_size[0] - crop_width

        if paste_y > original_size[1]-crop_height:
            paste_y = original_size[1]-crop_height
            
    return reconstructed_img

def main():
    rootDirSource = "dataset1/train"
    imageFiles = os.listdir(rootDirSource)
    imageFiles = list(filter(lambda x:"jpg" in x,imageFiles))
    print(len(imageFiles))
    for imageFile in imageFiles:
        maskFile = imageFile.split(".")[0] + "_mask.png"
        image_path = os.path.join(rootDirSource, imageFile)
        mask_path = os.path.join(rootDirSource, maskFile)
        
        img = Image.open(image_path).convert('RGB')
        mask = Image.open(mask_path).convert('L')

        crops = create_crops(img)
        reconstructed_image = reconstruct_image(crops, img.size)
        # reconstructed_image.show()
        cv2.imshow("reconstructed_image",np.array(reconstructed_image))
        
        cropsMask = create_crops(mask)
        reconstructed_mask = reconstruct_image(cropsMask, mask.size)
        cv2.namedWindow("reconstructed_mask", cv2.WINDOW_NORMAL)
        
        cv2.moveWindow("reconstructed_mask", 650, 0)  
        
        cv2.imshow("reconstructed_mask",np.array(reconstructed_mask))        
        cv2.waitKey(0)
    
    
    
main()