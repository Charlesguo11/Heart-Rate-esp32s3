import os
from capture_frames import get_file_content, client, imageType

path2 = '/home/gcl/rPPG-master/pending/'
datanames2 = os.listdir(path2)
for i in datanames2:
    file_path2 = '/home/gcl/rPPG-master/pending/' + i
    image = get_file_content(file_path2)
    # 人脸识别：标框和性别
    options = {}
    options["face_field"] = "gender"
    options["max_face_num"] = 10
    # 调用人脸识别函数
    result1 = client.detect(image, imageType, options)
    print("人脸识别结果：", result1)