
import base64
from contextlib import suppress
import json
import os

import boto3
import cv2
import numpy as np

bucketName = "upload-invoice"

s3resource = boto3.resource("s3")
s3client = boto3.client('s3')

class Utils:
    bucketName = "upload-invoice"

    s3resource = boto3.resource("s3")
    s3client = boto3.client('s3')

    ############################################
    def get_json_from_s3(file_name, bucket_name=bucketName):
        # print(f"get_file_from_s3: {file_name}")

        s3 = boto3.resource("s3")
        # s3.Bucket(bucket_name).get_object(Key=s3_path, Body=fs["file"].value)
        # Get the S3 object representing the file
        s3_object = s3.Object(bucket_name, file_name)

        # Read the contents of the file
        file_content = s3_object.get()['Body'].read().decode('utf-8')
        return json.loads(file_content)

    ############################################

    def getS3Bucket(bucket_name= bucketName):
        return s3resource.Bucket(bucket_name)

    ############################################
    def get_img_file_from_s3(file_name, bucketName = bucketName):
        # Get the S3 object representing the file
        s3_object = s3resource.Object(bucketName, file_name)

        # Read the contents of the file
        file_contents = s3_object.get()['Body'].read()
        base64_bytes = base64.b64encode(file_contents)
        imgBase64 = base64_bytes.decode('ascii')
        img_data = base64.b64decode(imgBase64)
        img_array = np.frombuffer(img_data, dtype=np.uint8)
        image = cv2.imdecode(img_array, cv2.IMREAD_COLOR) 
        return image
    ############################################

    def is_single_color_path(gray_patch: np.ndarray, epsilon=2.5):
        gray_patch = gray_patch.copy()
        # Convert the patch to grayscale
        with suppress(Exception):
            gray_patch = cv2.cvtColor(gray_patch, cv2.COLOR_BGR2GRAY)

        # Sample pixels to reduce noise
        sampled_patch = gray_patch
        # Calculate the standard deviation of the pixel intensities
        std_dev = np.std(sampled_patch)

        # Check if the standard deviation is below the epsilon threshold
        return std_dev, std_dev < epsilon  # The patch is nearly a single color


    def is_single_color_img(img, patch_size_percent=0.1):
        """
        Extracts a patch of size `patch_size_percent` of the image from the bottom left corner.

        Args:
            img: A NumPy array representing the image.
            patch_size_percent: A float between 0 and 1 representing the percentage of the 
                                original image size to use for the patch. Defaults to 0.1 (10%).

        Returns:
            A NumPy array representing the extracted patch.

        Raises:
            ValueError: If `patch_size_percent` is less than 0 or greater than 1.
        """

        if patch_size_percent < 0 or patch_size_percent > 1:
            raise ValueError("patch_size_percent must be between 0 and 1")

        img_height, img_width = img.shape[:2]  # Get height and width from the first two dimensions
        patch_height = int(img_height * patch_size_percent)
        patch_width = int(img_width * patch_size_percent)

        # Bottom left corner starting point
        start_y = img_height - patch_height
        start_x = 0  # Assuming bottom left corner

        # Extract the patch using slicing
        bottomLeftPatch = img[start_y:, start_x:start_x + patch_width]

        # Top right corner starting point (top left corner of the patch)
        start_y = 0
        start_x = img_width - patch_width  # Adjusted for right corner

        # Extract the patch using slicing
        topRightPatch = img[start_y:start_y + patch_height, start_x:]
        
        return Utils.is_single_color_path(bottomLeftPatch) and Utils.is_single_color_path(topRightPatch)
    
    
    ###
    def count_all_files(folder_path):
        """
        Counts all files in the specified folder.

        Args:
            folder_path: The path to the folder containing the files.

        Returns:
            An integer representing the number of files in the folder.
        """
        try:
            num_files = len(os.listdir(folder_path))
            return num_files
        except FileNotFoundError:
            print(f"Error: Folder not found: {folder_path}")
            return 0    