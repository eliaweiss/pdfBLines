
import json
import os
import cv2

from utils import Utils as U

MAX_DOCS =  100
def main():
    with open("processedFiles.json", "r") as f:
        processedFiles = json.load(f)
    trainImagesPath = "trainImages"
    paginator = U.s3client.get_paginator('list_objects_v2')  # Use paginator for large buckets

    for page in paginator.paginate(Bucket=U.bucketName):
        if len(os.listdir(trainImagesPath)) > MAX_DOCS:
            break
        if 'Contents' in page:
            for obj in page['Contents']:
                if len(os.listdir(trainImagesPath)) > MAX_DOCS:
                    break                
                if obj['Key'].endswith('.pdf'):
                    if obj['Key'] in processedFiles["processedFiles"]:
                        continue
                    
                    addToProcessedFiles(processedFiles, obj)
                        
                    fileName = obj['Key'].split(".")[0]
                    resJsonFName =  f"{fileName}.res.json"
                    try:
                        resJson = U.get_json_from_s3(resJsonFName)
                        # if 'docType' in resJson:
                        if 'receiptNumbers' not in resJson:
                            continue
                            
                        fileNameFull = fileName+'.jpg'
                        image = U.get_img_file_from_s3(fileNameFull)
                        h,w =  image.shape[:2]
                        if h>1.5*w:
                            continue
                        if U.is_single_color_img(image):
                            imgPath = os.path.join(trainImagesPath,fileNameFull)
                            cv2.imwrite(imgPath,image)
                            
                            # cv2.imshow("image", image)
                            # cv2.waitKey()
                    except Exception as e:
                        pass
                        

def addToProcessedFiles(processedFiles, obj):
    processedFiles["processedFiles"].append(obj['Key'])
    with open("processedFiles.json", "w") as f:
        f.write(json.dumps(processedFiles))
                    
                    # pdf_objects.append(obj)
                    
main()