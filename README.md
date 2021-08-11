# 版权说明
本项目fork自[Johnserf-Seed TikTokDownload](https://github.com/Johnserf-Seed/TikTokDownload)。目的是为了增加个性化的功能，若想体验更多完善的功能请支持原作者的项目。

# 环境要求
- 请检查宿主机，是否安装了python环境，并且配置了环境变量
~~~
    python --version 
~~~
![python环境](./Resource/python.jpg)

- 请下载以下python库
~~~
    pip install requests
    pip install retrying
~~~

# 功能
- [x] 全量下载：下载指定博主主页下所有的无水印视频和图片
- [x] 增量下载：下载之前下载过全量的博主新更新的内容

1. 建议先使用全量下载功能，先下载一遍全部视频。
2. 再使用增量下载功能，定期下载即可。（全量下载以后，会将当前博主放到增量下载列表里，选择增量下载功能时，无需再复制链接）

# 使用方法
目前只支持源码运行，等功能完善后，再封装docker

## 1. Docker 
敬请期待

## 2. 源码运行

2.1 请下载源码，在终端运行以下命令，进入程序。

~~~
python TikTokMulti.py
~~~
![python环境](./Resource/guide.jpg)

2.2 若选择功能1，需要先复制抖音博主主页地址

![step1](./Resource/userHomeStep1.jpg)
![step2](./Resource/userHomeStep2.png)
![step3](./Resource/userHomeStep3.png)

2.3 复制地址，进行下载。
ps:若遇到报错，请重新下载。基本上是服务器抽风

![step3](./Resource/fullDownload.jpg)

2.4 文件保存在Download文件里，以名称分类

![python环境](./Resource/download.jpg)

# 说明

- 增量下载功能是根据Download文件里有无相同名称的视频来判断的，所以建议不要删除此文件夹里的视频，否则增量下载功能将失效。