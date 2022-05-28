import os
import cv2
import numpy as np
import torch
from torch import nn

from client import getFramFromCamera, take_picture
from models import LinkNet34
import torchvision.transforms as transforms
from torch.autograd import Variable
from PIL import Image, ImageFilter
import time
import sys
import base64
from aip import AipFace
import schedule

APP_ID = '26287441'
API_KEY = 'UtHQhPxB9xhWLNjGjynNN8W7'
SECRET_KEY = 'uW2wWVRGKcknvDAdwn1GdwkmHwEZi4qZ'
client = AipFace(APP_ID, API_KEY, SECRET_KEY)
imageType = 'BASE64'


def get_file_content(file_path):
    """获取文件内容"""
    with open(file_path, 'rb') as fr:
        content = base64.b64encode(fr.read())
        return content.decode('utf8')


def face_register():
    path1 = '/home/gcl/rPPG-master/list/'
    datanames1 = os.listdir(path1)
    for i in datanames1:
        file_path1 = '/home/gcl/rPPG-master/list/' + i
        image1 = get_file_content(file_path1)
        groupId = "group1"
        userId = os.path.splitext(i)[0]
        """ 调用人脸注册 """
        result = client.addUser(image1, imageType, groupId, userId)
        # print(result)


def face_detect():
    global username
    username = 'none'
    file_path2 = '/home/gcl/rPPG-master/test.jpg'
    image = get_file_content(file_path2)
    # 人脸识别：标框和性别
    options = {}
    options["face_field"] = "gender"
    options["max_face_num"] = 10
    # 调用人脸识别函数
    result1 = client.detect(image, imageType, options)
    print("人脸识别结果：", result1)
    # 人脸搜素
    groupIdList = "group1"
    options = {}
    options["max_face_num"] = 5
    options["match_threshold"] = 70
    result2 = client.multiSearch(image, imageType, groupIdList, options)
    print("人脸搜索结果：", result2)
    scoremax = 0
    username = "null"
    for item in result2['result']['face_list']:
        if item['user_list']:
            for user in item['user_list']:
                if user["score"] > scoremax:
                    scoremax = user["score"]
                    username = user['user_id']
    return username


def face_recoginition():
    name = face_detect()
    with open("name.txt", "w") as f:
        f.write(str(name))


class CaptureFrames():

    def __init__(self, bs, source, show_mask=False):
        self.frame_counter = 0
        self.batch_size = bs
        self.stop = False
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.model = LinkNet34()
        self.model.load_state_dict(torch.load('linknet.pth'))
        self.model.eval()
        self.model.to(self.device)
        self.show_mask = show_mask
        face_register()

    def __call__(self, pipe, source):
        self.pipe = pipe
        self.capture_frames(source)

    def capture_frames(self, source):

        img_transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        # schedule.every(10).minutes.do(face_recoginition)  # 每隔十分钟执行一次任务
        # camera = cv2.VideoCapture(0)
        take_picture()
        face_recoginition()
        time.sleep(1)
        self.model.eval()
        grabbed = True
        time_1 = time.time()
        self.frames_count = 0
        while grabbed:
            frame = getFramFromCamera()
            orig = frame
            if not grabbed:
                continue
            global num
            shape = orig.shape[0:2]
            frame = cv2.cvtColor(orig, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (256, 256), cv2.INTER_LINEAR)
            a = img_transform(Image.fromarray(frame))
            a = a.unsqueeze(0)
            imgs = Variable(a.to(dtype=torch.float, device=self.device))
            pred = self.model(imgs)

            pred = torch.nn.functional.interpolate(pred, size=[shape[0], shape[1]])
            mask = pred.data.cpu().numpy()
            mask = mask.squeeze()

            # im = Image.fromarray(mask)
            # im2 = im.filter(ImageFilter.MinFilter(3))
            # im3 = im2.filter(ImageFilter.MaxFilter(5))
            # mask = np.array(im3)

            mask = mask > 0.8
            orig[mask == 0] = 0
            self.pipe.send([orig])

            #if self.show_mask:
            #    cv2.imshow('mask', orig)

            if self.frames_count % 30 == 29:
                time_2 = time.time()
                sys.stdout.write(f'\rFPS: {30 / (time_2 - time_1)}')
                sys.stdout.flush()
                time_1 = time.time()
            self.frames_count += 1


    #def terminate(self, camera):
    #    self.pipe.send(None)
    #    cv2.destroyAllWindows()
    #    camera.release()
