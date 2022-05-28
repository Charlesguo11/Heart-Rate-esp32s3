
> 提示：该项目建立于ubuntu18.04版本，esp-idf版本为4.4.1，ESP32S3-EYE开发板由乐鑫公司提供，在此表示感谢。项目中的rPPG技术来源于github上的nasir，本项目所有代码均已开源放置于github中，链接在文章底部可以找到

@[TOC](文章目录)

---

# 前言

本文记录了物联网竞赛的项目开发全过程，包含了**ESP32S3-EYE**使用模块，**人脸识别和rPPG**代码模块，**数据库**连接模块，以及基于**APICloud**开发的软件模块

---

# 一、ESP32-S3-EYE模块
## 硬件部分

 1. **开发板简介**

	ESP32-S3-EYE 是一款小型人工智能开发板，搭载 ESP32-S3 芯片和乐鑫 AI 开发框架 ESP-WHO。开发板配置一个 2 百万像素的摄像头、一个 LCD 显示屏和一个麦克风，适用于图像识别和音频处理等应用。板上还配有 8 MB 八线 PSRAM 和 8 MB flash，具有充足的存储空间。此外，开发板上的 ESP32-S3 芯片还提供了 Wi-Fi 图传和 USB 端口调试等功能。

 2. **本项目使用部分**
 	摄像头：OV2640摄像头
 	LCD显示屏
 	Wi-Fi图传功能

## 软件部分

 1. **ESP-IDF环境搭建（ubuntu18.04）**
 
 	由于国内网速问题，下载esp-idf时都会遇到各种克隆失败的问题，为了解决这个问题，借鉴了一些博主的方法，总结了一下esp-idf稳定下载的方法：
```bash
//下载gitee工具
git clone https://gitee.com/EspressifSystems/esp-gitee-tools.git
//下载指定版本的esp-idf（此处采用稳定版本V4.4）
git clone -b release/v4.4 https://gitee.com/EspressifSystems/esp-idf.git
//进入工具目录，执行命令更新子模块（user部分为你的用户名）
cd esp-gitee-tools
./submodule-update.sh ~/user/esp/esp-idf
```
 2. **ESP-WHO下载和使用**
 
获取ESP-WHO
```bash
git clone --recursive https://github.com/espressif/esp-who.git
```
打开esp-who文件夹后打开esp-idf
```bash
cd esp-who
get_idf
```

设定目标芯片
```bash
idf.py set-target [SoC] #[SOC]替换成目标芯片，如esp32s3
```
编译并烧录程序（运行IDF监视器）

```bash
idf.py build
idf.py flash monitor
```

 3. **Micropython & Pycharm & ESP32s3 环境搭建**

 因为我们的代码主要以python语言为主，所以刚开始小组采用的是配置一个micropython固件，这样方便后续代码编写
 
（1）**配置pycharm环境**
	下载Micropython插件
	![在这里插入图片描述](https://img-blog.csdnimg.cn/1d93923ae0a94e87a77dde0677e50075.jpeg#pic_center)
配置Micropython接口，language->micropython->Enable micropython support，devicetype选择pybord（ESP32系列）device path选择esp32对应的接口：
*COM7*（Windows），*/dev/ttyACM0*（Ubuntu18.04）
![在这里插入图片描述](https://img-blog.csdnimg.cn/35c73f6fd1f844d5a185fe9b2547b940.jpeg#pic_center)
（2）**刷写ESP32S3固件**
1.下载刷写工具
Windows10：[esp刷写工具](https://www.espressif.com/zh-hans/support/download/other-tools?keys=&field_type_tid%5B%5D=13)
Ubuntu18.04: [esptool官方刷写工具](https://github.com/espressif/esptool)
2.micropython固件下载
[固件官网下载地址](https://micropython.org/download/)
根据自己的主控板选择对应的固件，注意下载".bin"格式的文件
3.开始刷写
首先进行擦除，其中/dev/ttyACM0为ubuntu系统中的接口地址
> esptool.py --chip esp32 --port /dev/ttyACM0 erase_flash

然后进行烧录，board-20210902-v1.17.bin为自己下载的固件（务必在有固件的文件夹中进行刷写，否则找不到固件）

> esptool.py --chip esp32s3 --port /dev/ttyACM0 write_flash -z 0 board-20210902-v1.17.bin

（3）将写好的程序烧录进芯片中
![在这里插入图片描述](https://img-blog.csdnimg.cn/0cb3d83265c343cab1fef339bcff34f6.jpeg#pic_center)
但是小组后面遇到一些网络连接问题，比如在尝试用Micropython中的WLAN模块实现WiFi连接时，出现无法连接的情况，因此最终决定在esp-idf的环境下进行编程

## 通信部分

 1. **传输方式确认**
**opencv的IP视频流传输测试:**
一开始项目尝试用opencv去基于IP地址看能否直接获取到摄像机的视频流。但是经过反复尝试以及各类资料查找之后，我们认为opencv的视频流传输是基于IP-CAMERA的。但是ESP32-S3的摄像头应当只是挂载在芯片上的一个设备，虽然提供了连接的IP，但是不符合opencv的该方法要求。
确定此点的来源是由于在opencv的接收当中会指定一个URL，其内部有着用户名称和密码。然而在ESP32-S3配置过程中，没有涉及到该点。
**基于网页抓取的图片获取测试:**
项目萌生过采用python的网页抓取的技术将图片抓取到本地算法进行运行的思路。虽然该方法简单易执行，但是需要打开网页进行操作。这一特点有些违背了物联网的初衷，也同时没有发挥芯片的作用。
**wireshack抓包分析和方法确定:**
由于ESP32-S3提供的ESP-WHO示例当中有着能够在网页端的摄像机画面流获取。因此我们萌生出了同样的想法，基于此示例去进行我们的传输编写。
该方法需要解决以下问题：网页对芯片发回的数据处理成了什么格式？网页如何同芯片建立起的传输？芯片发回给网页的报文是什么格式？我们如何编写自己的传输方式？
(1)网页呈现格式的确定:
ESP32-S3的摄像头应当是OV2640的版本,在网页运行的情况下，其传输的呈现框位置和元素如下：
![在这里插入图片描述](https://img-blog.csdnimg.cn/a02ddd327add497fbb16034398ac1868.png#pic_center)
其实际上将接收到的数据设置为了img元素，即网页端也不是通过视频流直接显示，而是通过了某种报文将摄像头的画面存到了报文当中，再将其传送给网页解析。
(2)传输报文的确定：
由于在网页当中进行元素审查和脚本查找并不方便，所以我们根据该文件名字，在/esp-who/components/web/www下找到了index_ov2640.html即网页的源码。
![在这里插入图片描述](https://img-blog.csdnimg.cn/a4b62a1dd65343ce916aed7ef3565e5f.png#pic_center)
同时，由于当前的文件夹下有着app_httpd和app_wifi的文件，我们敲定：该网站是要通过芯片联网之后，通过httpd的报文将其传输到网页端进行解析的。由于httpd实际就为apache下的http协议，所以我们的初步思路就为：可否截取芯片发送的报文？
这一思路需要我们进行发送报文的确定，然而由于芯片代码实际上是写死的，那其就相当于一个服务器，而我们只需要模拟用户端向其发送报文即可获得其返回的相机帧。
该点我们最终通过wireshack的抓包进行。思路如下：
1、先打开wireshack，让其接受一段时间的计算机报文，大致确定没有流传输的情况下报文的情况
![在这里插入图片描述](https://img-blog.csdnimg.cn/2e354d481dd44e4b9347ca3b419b1cf8.png#pic_center)
2、随后，点击网页端的传输流开启按钮，再在wireshack当中看此时的报文特点。经过比对，我们发现在网页端显示的 IP为172.20.10.5的时候，以此为参考出现了大量的172.20.10.5和172.20.10.6的报文。由此，我们初步推测，该视频流的传输是建立在该两个IP上的传输。
3、将wireshack重启，重新获取报文，此时输入筛选条件ip.src=172.20.10.5 && ip.dst==172.20.10.6，之后，点击一次开始流传输之后立马点击关闭，wireshack当中出现了不少符合条件的报文。由于http实际基于tcp传输，则tcp一定会有一个建立传输的握手过程，通过源IP和目标IP的相互调换和调整，找到发出tcp连接请求的报文，即内容为SYN的报文，其源IP就是连接的请求端。通过这一方法我们确认了172.20.10.5为服务器端（芯片），172.20.10.6为客户端（网页）
4、通过客户端的发送报文，我们找到了触发芯片发送的HTTP报文如下：
![在这里插入图片描述](https://img-blog.csdnimg.cn/0c0ea2966a634fe18d292ac4e9de3199.png#pic_center)
即我们需要在程序内发送该报文，然后就能接收到来自芯片的流信息。且同时根据html的源码和报文的目标端口，我们确定了端口为81。即报文的传输目的地为172.20.10.5:81

 2. **芯片发送**
虽然ESP提供了socket，但是在层层深入之后，我们发现实际上调用的是<sys/socket.h>头文件进行的再一步封装。则我们直接采用socket。
由于我们只需要图片的比特信息，所以删除了全部的测试报文发送。只要是能够正确进行jpg解码的即ESP_OK的状态，我们就直接开始建立图片的收发socket，而建立起httpd连接的socket只起到一个能够正确进入到图片socket建立的工具而在图片的传输过程中废用。
同样，基于之前连接局域网的方式，我们推测实际芯片的另外函数当中，也是允许局域网内的全部设备连接的。所以我们将socket设置为INADDR_ANY即可不用写死芯片的连接IP。连接之后，发送两个报文，第一个发送帧长度即Byte数，第二个发送fram的比特数据。发送完后为了后续连接的正确建立，则直接关闭socket。等待下一个http get /stream的报文进入在进行下一次发送。虽然存在tcp的建立开销，但是在局域网内该开销同图片传输处理的开销相比可以忽略
如下完成一次帧传输：

```bash
        //解码成功的，创建socket
        int serveSocket;
        int clientSocket;
        struct sockaddr_in server_addr;
        struct sockaddr_in client_addr;
        socklen_t sin_size;
        memset(&server_addr,0,sizeof(server_addr)); //数据初始化--清零  
        server_addr.sin_family=AF_INET; //设置为IP通信  
        server_addr.sin_addr.s_addr=INADDR_ANY;//服务器IP地址--允许连接到所有本地地址上  
        server_addr.sin_port=htons(8888); //服务器端口号  
        /*创建服务器端套接字--IPv4协议，面向连接通信，TCP协议*/  
        if((serveSocket=socket(PF_INET,SOCK_STREAM,0))<0)  
        {    
            ESP_LOGE(TAG, "socket error");
            return 1;  
        }  
        /*将套接字绑定到服务器的网络地址上*/  
        if(bind(serveSocket,(struct sockaddr *)&server_addr,sizeof(struct sockaddr))<0)  
        {  
            ESP_LOGE(TAG, "bind error");
            return 1;  
        }  
        ESP_LOGE(TAG, "server scocket created");
        /*监听连接请求--监听队列长度为1*/  
        if(listen(serveSocket,1)<0)  
        {  
            ESP_LOGE(TAG, "listen error");
            return 1;  
        };  
        sin_size=sizeof(struct sockaddr_in);  
        if((clientSocket=accept(serveSocket,(struct sockaddr *)&client_addr,&sin_size))<0)  
        {  
            ESP_LOGE(TAG, "accept error");
            return 1;  
        }  
        ESP_LOGE(TAG, "sending pic size %d"， (int)_jpg_buf_len);  
        char lenStr[128];
        itoa(_jpg_buf_len,lenStr,10);
        send(clientSocket,lenStr,strlen(lenStr),0);
        ESP_LOGE(TAG,"size was sent");  
        ESP_LOGE(TAG,"sending pic");  
        send(clientSocket,(char*)_jpg_buf,_jpg_buf_len*8,0);
        if((clientSocket=accept(serveSocket,(struct sockaddr *)&client_addr,&sin_size))<0)  
        {  
            ESP_LOGE(TAG, "accept error");
            return 1;  
        }  
        ESP_LOGE(TAG, "all recieved");  
        close(serveSocket);
```

 3. **算法接收**
由于算法端实际为python，则需要进行python的socket连接建立。关键代码如下：

```bash
import socket

'''建立连接，进入httpd的函数内部确保socket能够脸上'''
url = '172.20.10.5'#局域网ip
port = 81#固定端口
http_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#连接到芯片
http_sock.connect((url, port))
request_url = 'GET /stream HTTP/1.1\r\nHost: 172.20.10.5\r\nConnection: close\r\n\r\n'
http_sock.send(request_url.encode())

'''图片传输socket'''
#连接
port = 8888
pic_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
pic_sock.connect((url, port))
#接收长度socket
arrayLength = int(pic_sock.recv(10000));
byteStreamLength = 8*arrayLength;
#接收比特
picByteStream = pic_sock.recv(byteStreamLength);
#通过比特流方式写入文件
image = open("test.jpq", "wb");
for i in range(0,arrayLength):
    image.write(picByteStream[i].to_bytes(1,byteorder="little",signed=False));
# 连接断开
pic_sock.close();
http_sock.close();
```
即先建立一个socket，向目标芯片发送sokcet包含报文'GET /stream HTTP/1.1\r\nHost: 172.20.10.5\r\nConnection: close\r\n\r\n'以触发流服务函数，随后建立socket获取Byte信息，再将长度信息乘以8之后得到正确的01流长度。通过01流长度获取socket内部的比特流之后写入到我们的本地test.jpg当中。
由于jpg实际应当不存储像素值，我们无法直接通过比特流获取到各个像素的RGB信息，所以不得不写入到文件当中再进行读取的方式以达到获取后续算法需要的颜色信息。

 4. **最终结果**
![在这里插入图片描述](https://img-blog.csdnimg.cn/6160b827e3e14b968e3588b44af4c8e7.png#pic_center)
**左半部分**表示在芯片接收到计算机传送图片的请求后，首先传输图片二进制流长度，计算机端受到后继续传输图片内容，之后计算机端会发送一个确认指令，代表图片长度及内容均已受到，之后才可以进行下一张图片的传输
**右半部分**表示程序首先进行初始化，进行人脸注册操作，再进行人脸检测得到用户姓名，之后开始识别心率，并显示每秒的帧数
**中间图表**的上半部分表示脉搏波数据，下半部分表示心率数据，同时实时心率将会显示在左上角HR处
 
---

# 二、人脸识别和心率检测
## 人脸识别
人脸识别部分采用百度API实现人脸注册以及人脸识别，使用前搜索百度AI创建自己的人脸识别项目，实名注册后便可以免费使用了，具体使用方法可以参考百度AI中的技术文档：

本项目中使用的代码如下：

```python
def face_register():#人脸注册
    path1 = '/home/gcl/rPPG-master/list/'
    datanames1 = os.listdir(path1)
    for i in datanames1:
        file_path1 = '/home/gcl/rPPG-master/list/' + i
        image1 = get_file_content(file_path1)
        groupId = "group1"
        userId = os.path.splitext(i)[0]
        """ 调用人脸注册 """
        result = client.addUser(image1, imageType, groupId, userId)
        
def face_detect():#人脸检测
    global username
    username = 'none'
    path2 = '/home/gcl/rPPG-master/pending/'
    datanames2 = os.listdir(path2)
    for i in datanames2:
        file_path2 = '/home/gcl/rPPG-master/pending/01.jpg'
        image = get_file_content(file_path2)
        # 人脸识别：标框和性别
        options = {}
        options["face_field"] = "gender"
        options["max_face_num"] = 10
        # 调用人脸识别函数
        result1 = client.detect(image, imageType, options)
        # 人脸搜素
        groupIdList = "group1"
        options = {}
        options["max_face_num"] = 5
        options["match_threshold"] = 70
        result2 = client.multiSearch(image, imageType, groupIdList, options)
        scoremax = 0
        username = "null"
        for item in result2['result']['face_list']:
            if item['user_list']:
                for user in item['user_list']:
                    if user["score"] > scoremax:
                        scoremax = user["score"]
                        username = user['user_id']
        return username
        
def face_recoginition():#人脸识别
    image = cv2.VideoCapture('rtsp://172.20.10.5')
    ret, frame = image.read()
    if ret:
        cv2.imwrite(r"/home/gcl/rPPG-master/pending/01.jpg", frame)
        name = face_detect()
        with open("name.txt", "w") as f:
            f.write(str(name))
```
代码主要分为人脸注册函数、人脸检测函数以及人脸识别函数，首先将需要注册的人脸图片（图片命名为该人的姓名）放置于list文件夹中，执行该函数时，会将list文件夹中的人脸加入百度AI的人脸库中（库名为group1），其次对保存在pending文件夹中的一张图片进行识别，在与人脸库中的人脸对比后，若相似度大于70，则返回其姓名，该部分由人脸识别函数进行调用
## rPPG非接触式心率检测

 1. **rPPG算法**
 	该方法利用相机对人面部进行拍摄，并估计人体心率。由于人体外周组织的血容量会影响光的透射或反射，并且人体血液对光的吸收会有脉动性的变化，所以导致人面部有伴随心跳节律持续的颜色变化，因此通过相机捕捉该变化再利用信号处理的方法就可以估计人体实时心率，该算法分为前后两个部分，首先进行人脸检测追踪，对每一帧摄像头传入的图像进行人脸提取，提取出人类脸上血液最丰富的区域，之后则只对此部分进行处理。之后提取rPPG信号，由每一帧图片的面部ROI生成RGB三通道信号，再从中进一步提取处脉搏波信号，通过提取出的脉搏波信号进行心率计算
 2. **使用方法**

```bash
git clone https://github.com/nasir6/rPPG.git
cd rPPG
pip install -r requirements.txt #下载项目所需要的安装包依赖
python3 run.py --source=0 --frame-rate=25 #以每秒25帧的速率运行
```
可能遇到的错误：
> magic_number = pickle_module.load(f, **pickle_load_args)

通过网上查找错误原因得到，可能是预训练模型出错，但将/home/gcl/.cache/torch/hub/checkpoints中找到的resnet34模型删除后，再次运行只是将这个模型再下了一遍，依然出现上述报错，因此推断此模型在github网站上可能并不稳定，暂时没有解决方案，我采用的是将windows系统中的linknet.pth移植到ubuntu即可，原linknet.pth为一个带有网址的文件，linknet.pth是作者的预训练模型，推测可能github上的模型已经损坏

 3. **运行结果**
 
 ![在这里插入图片描述](https://img-blog.csdnimg.cn/783477e2af6448a2b42556e7c9923ffd.png#pic_center)


---

# 三、数据库连接
## 服务器部署

 1. **必要性**
	由于项目当中需要通过ESP的终端机器获取到心跳信息并且进行在手机端的的呈现，则涉及到数据流转的问题。倘若不部署服务器，则对于心率的识别只能在移动端本地进行。而这一点实际为不现实的。无论是从代码的编写难度和对手机处理器的考验都是极大的。
同时，由于数据存储的需要，我们不能使用本地数据库进行数据的查询和存储，这样会损失掉物联网中各终端数据共享同步的意义。所以租赁服务器是十分必要的
 2. **选择**
	在前期的部署测试当中，选择过华为云和腾讯云两种。
腾讯云优势在于：其直接提供了数据库mysql的模块和云服务模块，环境配置较为简单直接。但其缺点在于：虽然云服务器为按量收费，但是mysql的数据库服务为分开收费，且为一小时一次。这使得总体的开销极大。
华为云缺点在于：缺点在于mysql的环境需要自己进行配置。而其优点在于：云服务器界面简洁，配置方便，而且云服务器同样也是按量收费，但是由于mysql的服务是自己进行配置，则不需要另行的费用。且其安全组和VPC的配置简洁直观。
综上，我们选择了华为云的服务器
 3. **初始配置过程**
VPC：
<table><tbody>
    <tr>
        <th>名称</th><th>IPv4网段</th><th>状态</th><th>子网个数</th><th>路由表</th><th>服务器个数</th>
    <tr>
        <td><font >vpc-heartRate</font></td><td><font >192.168.0.0/16 (主网段)</font></td><td >可用</td><td >1</td><td >1</td><td >1</td>
</table>

SG安全组：
![在这里插入图片描述](https://img-blog.csdnimg.cn/4c69054510394d2c8143f10603e98c7f.jpeg#pic_center)
同时，由于后续会在其上部署mysql，则在入方向规则当中，允许3306端口的访问
<table><tbody>
    <tr>
        <th>优先级</th><th>策略</th><th>协议端口</th><th>类型</th><th>源地址</th><th>描述</th>
    <tr>
        <td><font >1</font></td><td><font >允许</font></td><td >TCP : 3306</td><td >IPv4</td><td >0.0.0.0/0</td><td >允许数据库的链接</td>
</table>

---
## 数据库部署
在开启服务器的情况下，进入其远程cloudShell

![在这里插入图片描述](https://img-blog.csdnimg.cn/04e6692173f7412296a6faa0fa91f6e6.png#pic_center)
通过以下指令进行mysql的配置：

```bash
apt-get update （更新数据源）
apt-get install mysql-server （安装mysql服务端）
mysql_secure_installation （确认权限）
```
配置完成后进入sql界面如下如下：

![在这里插入图片描述](https://img-blog.csdnimg.cn/923eed1f55e04b8bbde78c2f20c99273.png#pic_center)
随后，按照以下指令进行用户权限的赋予

```bash
mysql> create user 'userName'@'%' identified by 'pwd'; （创建用户，并指定密码）
mysql> grant all privileges on *.* to 'userName'@'%'; （为该用户授予全部表的访问权限）
```
配置完成之后，进行sql的用户查询语句结果应当如下：
![此处将最高权限赋予了allQualified用户](https://img-blog.csdnimg.cn/b3d835fc6d434f39a55a927f3c15541d.png#pic_center)
此处将最高权限赋予了allQualified用户。至此，服务端配置完成

---
# 四、程序开发模块
## 开发环境

 1. **APICloud**
	APICloud为一个 lowcode的手机端软件开发平台。其下有着丰富的的组件可以进行调用。提供高效的APP开发、手机APP制作与APP管理等服务
 2. **APICloud Studio**
	为APICloud配套的IDE。其类似于vscode，但是集成了git的代码管理以及APICloud的在线编译为
 3. **安卓雷电模拟器**
 	雷电模拟器是一款可以让手机应用及游戏在电脑上运行的软件，采用虚拟安卓手机操作界面，实现安卓应用的安装、使用、卸载。

## 开发语言

 - **HTML**
	超文本标记语言，标准通用标记语言下的一个应用。 “超文本”就是指页面内可以包含图片、链接，甚至音乐、程序等非文字元素。 超文本标记语言的结构包括“头”部分、和“主体”部分，其中“头”部提供关于网页的信息，“主体”部分提供网页的具体内容。
 - **CSS**
	一种用来表现HTML或XML文件样式，用于增强控制网页样式并允许将样式信息与网页内容分离的一种标记性语言。
## 开发逻辑

 - 先利用平台构造一个基础的APP模板，所有选项都使用默认选项

 - 设置APP初始图标以及启动页面。图片可以通过网络获取，并传入程序

 - 设置APP的基础格式，页眉和页脚的属性以及样式等参数

 - 设置页面的基础属性、包括各元素的基础样式等
 *该部分使用一些基础的CSS语言以及apicloud所以提供的API的接口进行实*

 - 设置基础背景样式，背景颜色、透明度、图案等属性

 - 加入折线图模块，用于显示心率数据，并对折线图进行编辑，增加坐标轴、显示横线等，提升折线图的美观度
 *为了应对可能存在一些设备无法通过api.frameWidth和api.frameHeight的方式获取到当前的框架长度，显示区域的设置有着两套方案。一套是按照设计地宽度进行定值初始化，一个是按照自适应的百分比方式进行初始化
同时，UI组件和html组件可能存在当输入框出现的时候重叠的情况，所以每次聚焦到输入框的时候，将UI的按钮先进行隐藏以防止遮挡的思路进行输入*
```bash
function fnOpen(){
   chart.open(
   {
    rect : {x : 50,y : 130,w : 510,h : 350},
           bg : '#FFFFFF',
           coordinate : {
           yAxis : {max : 125,min : 0,step : 25,width : 40,size : 12,color : '#FF5255'},
           xAxis : {max:24,min: 0,step:6,minStep : 1,minStepGap:20,height : 30,size : 12,color: '#FF5255'},
           border : {size : 0.5,color : '#52FF55'},
           brokenLine : {color : '#FF5255',width : 2.5}},
           shadow : [],
           datas : cors,
           fixedOn : api.frameName}, 
		   function(ret) {
           if (ret) {
           chartID = ret.id;//打开成功之后，对图表的id进行赋值
           }});
   }
```

 - 编写数据获取函数和显示函数，用于获取心率的数据和将数据显示到折线图上

```bash
function updateCors(){
    //如果已经建立了连接
    if(database.isConnected()){
    //模拟数据更新
    var heartRate = Math.floor(Math.random()*25+50);//随机生成50-75的取整心率数据
    database.update(
    {sql: "insert into heartRate values('gcl',"+heartRate+", now());"},
    function(ret){}
    )//插入到数据库当中，插入的表项是（用户名，心率，sql自带的当前时间函数 ）
    //查找心率
    database.query(
    //从表中查找用户ID是gcl的心率
    {sql: "select rate from heartRate where userID ='xxx';"},
    function(ret){ 
    //回调函数
    //从返回的JSON文件当中取出result结果集
    var heartRateSet = ret["result"];
    //由于可能存在查到一半数据库就关闭了，判断结果集有没有元素
    if(heartRateSet!=[]){
    //有元素，将存储坐标的cors数组进行初始化
    cors=[];
    for(i=0;i<heartRateSet.length;i++){
        var x = i;
        var y = heartRateSet[i]["rate"];//取出结果集当中存储的数据库表当中，“rate”对应的数字即心率
        cors.push({xValue: x, yValue: y});//按照api需要的格式插入到坐标数组}
   }})}}
```

 - 编写主函数，整理各变量以及函数的前后关系，保证程序运行方式合理。同时加入初始化函数，使各个元素能正常运转
 - 加入按钮模块，对按钮的属性、功能进行调整，使其能达到我们的目的。同时在head和主函数apiready中加入相应的基础设置和初始化函数

```bash
function UIButton_open() {
   btn1.open({
              rect: { x: 47,y: 550,w: 515,h: 50 },
              corner: 5,
              border:{ borderColor: 'FF5474',borderWidth: '0' },
              bg: {normal: '#FFFFFF',
                   highlight: '#B6B6B6',
                   active: '#FFFFFF'},
              title: {size: 14,highlight: '隐藏折线图',active: '隐藏折线图',normal: '隐藏折线图',highlightColor: '#0D0D0D',
              activeColor: '#0D0D0D',normalColor: '#0D0D0D',alignment: 'center',},
              fixedOn: api.frameName,
              fixed: true,
      		  move: true},
function(ret, err) {
			  if (ret) {fnHide} 
   			  else {alert(JSON.stringify(err));}
              });
```

 - 调整各个元素整体布局。增加界面的美观性
 - 增加其他功能，并调整相应的属性和布局

## 使用模块
（1）mySQL模块：集成JDBC，可以连接MySQL数据库。用于在手机移动端和数据库建立数据通信和连接。
（2）UIButton模块：UIButton 是 button 模块的优化升级版，用原生代码实现了一个可自定义的按钮，开发者使用此模块可以实现在一个模块视图上添加自定义按钮的功能，本模块支持手指拖动改变按钮位置功能。
（3）divisionalLineChart模块：divisionalLineChart模块封装了一个折线图视图，开发者可自定义其样式，可刷新数据，左右拖动查看不同的数据，并且能响应用户点击结点的事件。
## 组件交互逻辑
![在这里插入图片描述](https://img-blog.csdnimg.cn/ab6ba7416ae346d2a3662a23b22bcbd9.png#pic_center)


