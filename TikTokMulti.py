import requests
import json
import os
import time
import configparser
import re
import sys
import TikTokDownload


class TikTok():
    #初始化
    def __init__(self,downloadType):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36 Edg/87.0.664.66'
        }

        #绘制布局
        print("#" * 130)
        print(
            """
                                                TikTokDownloadTool
    软件说明：
            1. 本项目fork自Johnserf-Seed的TikTokDownload。目的是为了增加个性化的功能，若想体验更多完善的功能请支持原作者的项目。
               https://github.com/Johnserf-Seed/TikTokDownload
            2. 如有您有任何bug或者意见反馈请在 https://github.com/creatorMao/TikTokDownloadTool/issues 发起

    功能清单：
            1. 全量下载：下载指定博主主页下所有的无水印视频和图片
            2. 增量下载：下载之前下载过全量的博主新更新的内容
    """
        )
        print("#" * 130)
        print('\r')

        #获取当前目录
        self.root_dir= os.path.dirname(__file__)

        #实例化读取配置文件
        self.cf = configparser.ConfigParser()

        #用utf-8防止出错
        self.cf.read(self.root_dir+"/conf.ini", encoding="utf-8")

        #读取保存路径
        self.save = self.cf.get("save", "url")

        #读取下载视频个数
        self.count = int(self.cf.get("count", "count"))

        #读取下载是否下载音频
        self.musicarg = self.cf.get("music", "musicarg")

        #读取用户主页地址
        self.userInput = '2' if downloadType!='' else input('请选择一种功能(输入功能的序号):')

        #读取下载模式
        self.mode = self.cf.get("mode", "mode")

        #保存用户名
        self.nickname = ""

        #用户主页地址前缀
        self.userHomePagePrefix = self.cf.get("api", "userHomePagePrefix")

        #用户主页地址样例
        self.userHomePageExmple = self.cf.get("api", "userHomePageExmple")

        #增量更新用户列表
        hisIncrementalUpdateUserList=self.cf.get("url", "incrementalUpdateUserList")
        self.incrementalUpdateUserList = [] if hisIncrementalUpdateUserList=="" else hisIncrementalUpdateUserList.split(',')

        if self.userInput == '1':
            self.uid = input(
                '请输入完整的个人主页地址(例如'+self.userHomePageExmple+'):')

            if self.uid=="":
                print("你在干什么,地址不能为空的哦！")
                return

            self.end = False
            linkFlag=self.judge_link((self.userHomePagePrefix+self.uid), False)

            if linkFlag==False:
                print("输入的地址不正确")
                return

            print('')
            print('全量下载已完成！')   

            userChoose=input('是否需要将此博主加入到增量下载列表？(回车默认加入，输入任意文字代表不加入):')
            if userChoose=='':
                currentUser=self.uid.replace(self.userHomePagePrefix, '')
                if currentUser not in hisIncrementalUpdateUserList:
                    self.cf.remove_section("url")
                    self.cf.add_section("url")
                    self.cf.set("url", "incrementalUpdateUserList", (hisIncrementalUpdateUserList + ("" if hisIncrementalUpdateUserList == "" else ",")+currentUser))
                    self.cf.write(open(self.root_dir+'/conf.ini', "w"))
                print('已将该博主，放入到增量下载列表中。下次你可选择功能2(增量下载),来下载该博主新更新的内容。');            
                     
        elif self.userInput == '2':
            updateLength=len(self.incrementalUpdateUserList)
            
            if updateLength==0:
                print("增量更新列表为空，请先选择功能1，进行一次全量更新以后，再选择增量更新！")
                return

            print('本次增量更新总共有'+str(updateLength)+"个用户")
            for idx in range(updateLength):
                print("")
                print("正在更新第"+str(idx+1)+"个用户")
                self.end = False
                self.judge_link(
                    (self.userHomePagePrefix+self.incrementalUpdateUserList[idx]), True)
            
            print('')
            print('增量下载已完成！')
        else:
            print("你在干什么，请输入正确的功能序号！")
            return

    #匹配粘贴的url地址
    def Find(self, string):
        # findall() 查找匹配正则表达式的字符串
        url = re.findall(
            'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)
        return url

    #判断个人主页api链接
    def judge_link(self, userId, isUpdateFlag):
        #获取解码后原地址
        r = requests.get(url=self.Find(userId)[0])
        multi_url = 'https://www.douyin.com/user/'

        #判断输入的是不是用户主页
        if r.url[:28] == multi_url:
            print('----正在为您下载主页上的视频----\r')
            key = re.findall('/user/(.*?)\?', str(r.url))[0]
            if not key:
                key = r.url[28:83]
            #print('----'+'用户的sec_id='+key+'----\r')
        else:
            return False

        #第一次访问页码
        max_cursor = 0

        #构造第一次访问链接
        api_post_url = 'https://www.iesdouyin.com/web/api/v2/aweme/%s/?sec_uid=%s&count=%s&max_cursor=%s&aid=1128&_signature=PDHVOQAAXMfFyj02QEpGaDwx1S&dytk=' % (
            self.mode, key, str(self.count), max_cursor)
        self.get_data(api_post_url, max_cursor, userId, isUpdateFlag)
        return api_post_url, max_cursor, key

    #获取第一次api数据
    def get_data(self, api_post_url, max_cursor, userId, isUpdateFlag):
        #尝试次数
        index = 0
        #存储api数据
        result = []
        while result == [] and index <= 4:
            index += 1
            print('----正在进行第 %d 次尝试----\r' % index)
            time.sleep(0.3)
            response = requests.get(url=api_post_url, headers=self.headers)
            html = json.loads(response.content.decode())
            if self.end == False and 'aweme_list' in html.keys() and len(html['aweme_list']) > 0:
                #下一页值
                self.nickname = html['aweme_list'][0]['author']['nickname']
                print('[  用户  ]:'+str(self.nickname)+'\r')
                max_cursor = html['max_cursor']
                result = html['aweme_list']
                print('----抓获数据成功----\r')

                #处理第一页视频信息
                self.video_info(result, max_cursor, userId, isUpdateFlag)
            else:
                max_cursor = html['max_cursor']
                self.next_data(max_cursor, userId, isUpdateFlag)
                #self.end = True
                print('----此页无数据，为您跳过----\r')

        return result, max_cursor

    #下一页
    def next_data(self, max_cursor, userId, isUpdateFlag):
        #获取解码后原地址
        r = requests.get(url=self.Find(userId)[0])

        #获取用户sec_uid
        key = re.findall('/user/(.*?)\?', str(r.url))[0]
        if not key:
            key = r.url[28:83]

        #构造下一次访问链接
        api_naxt_post_url = 'https://www.iesdouyin.com/web/api/v2/aweme/%s/?sec_uid=%s&count=%s&max_cursor=%s&aid=1128&_signature=RuMN1wAAJu7w0.6HdIeO2EbjDc&dytk=' % (
            self.mode, key, str(self.count), max_cursor)
        index = 0
        result = []
        while self.end == False:
            #回到首页，则结束
            if max_cursor == 0  or index >= 4:
                self.end = True
                return
            index += 1
            print('----正在对', max_cursor, '页进行第 %d 次尝试----\r' % index)
            time.sleep(0.3)
            response = requests.get(
                url=api_naxt_post_url, headers=self.headers)
            html = json.loads(response.content.decode())

            if self.end == False:
                #下一页值
                max_cursor = html['max_cursor']
                result = html['aweme_list']
                print('----', max_cursor, '页抓获数据成功----\r')
                #处理下一页视频信息
                self.video_info(result, max_cursor, userId, isUpdateFlag)
            else:
                self.end == True
                print('----', max_cursor, '页抓获数据失败----\r')
                #sys.exit()

    #处理视频信息
    def video_info(self, result, max_cursor, userId, isUpdateFlag):
        #作者信息
        author_list = []

        #无水印视频链接
        video_list = []

        #作品id
        aweme_id = []

        #作者id
        nickname = []

        for i2 in range(len(result)):
            try:
                nick = str(result[i2]['author']['nickname'])
                title = str(result[i2]['desc'])
                id = str(result[i2]['aweme_id'])
                author_list.append(title)
                video_list.append(
                    str(result[i2]['video']['play_addr']['url_list'][0]))
                aweme_id.append(id)
                nickname.append(nick)

                ##图片下载
                if str(result[i2]['aweme_type']) == "2":
                    self.photos_download(title, id, nick, isUpdateFlag)

            except Exception as error:
                print(error)
                pass
        self.videos_download(author_list, video_list, aweme_id,
                             nickname, max_cursor, userId, isUpdateFlag)
        return self, author_list, video_list, aweme_id, nickname, max_cursor
    
    # 处理文件名称，如果太长则截取，只取50个字
    def dealFileName(self,name):
        if len(name)>=50:
            return name[0:50]
        return name

    #图片下载
    def photos_download(self, author_name, id, nickname, isUpdateFlag):
        try:
            #创建并检测下载目录是否存在
            os.makedirs(self.save + self.mode + '/' + nickname)
        except:
            #有目录不再创建
            pass
        try:
            # 官方接口
            jx_url = f'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={str(id)}'
            js = json.loads(requests.get(
                url=jx_url, headers=self.headers).text)
            images = js['item_list'][0]['images']
            for i in range(len(images)):
                imagesUrl = str(images[i]['url_list'][0])
                
                name=re.sub(r'[\\/:*?"<>|\r\n]+', "_", author_name)
                photoUrl = self.save + self.mode + '/' + nickname + '/' + name+ str(id)+str(i) + '.jpeg'
                photoShortUrl=self.save + self.mode + '/' + nickname + '/' + self.dealFileName(name)+ str(id)+str(i) + '.jpeg'

                if os.path.isfile(photoUrl) or os.path.isfile(photoShortUrl):
                    print("文件已下载，已为你跳过")
                    if isUpdateFlag == True:
                        return
                    continue
                
                print('开始下载图片'+photoShortUrl)

                photo = requests.get(imagesUrl)  # 保存图片
                if photo.status_code == 200:
                    with open(photoShortUrl, 'wb') as file:
                        file.write(photo.content)
                        print('图片下载成功')

        except Exception as error:
            print("图片下载错误："+error)

    def videos_download(self, author_list, video_list, aweme_id, nickname, max_cursor, userId, isUpdateFlag):
        for i in range(len(video_list)):
            try:
                #创建并检测下载目录是否存在
                os.makedirs(self.save + self.mode + '/' + nickname[i])
            except:
                #有目录不再创建
                pass

            try:
                if self.musicarg == "yes":  # 保留音频
                    # 官方接口
                    jx_url = f'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={aweme_id[i]}'
                    js = json.loads(requests.get(
                        url=jx_url, headers=self.headers).text)
                    music_url = str(js['item_list'][0]['music']
                                    ['play_url']['url_list'][0])
                    music_title = str(js['item_list'][0]['music']['author'])
                    music = requests.get(music_url)  # 保存音频
                    start = time.time()  # 下载开始时间
                    size = 0  # 初始化已下载大小
                    chunk_size = 1024  # 每次下载的数据大小
                    content_size = int(
                        music.headers['content-length'])  # 下载文件总大小
                    try:
                        if music.status_code == 200:  # 判断是否响应成功
                            print('[  音频  ]:'+author_list[i]+'[文件 大小]:{size:.2f} MB'.format(
                                size=content_size / chunk_size / 1024))  # 开始下载，显示下载文件大小
                            m_url = self.save + self.mode + '/' + nickname[i] + '/' + re.sub(
                                r'[\\/:*?"<>|\r\n]+', "_", music_title) + '_' + author_list[i] + '.mp3'
                            with open(m_url, 'wb') as file:  # 显示进度条
                                for data in music.iter_content(chunk_size=chunk_size):
                                    file.write(data)
                                    size += len(data)
                                    print('\r'+'[下载进度]:%s%.2f%%' % (
                                        '>'*int(size*50 / content_size), float(size / content_size * 100)), end=' ')
                                end = time.time()  # 下载结束时间
                                print('\n' + '[下载结果]:已下载，耗时: %.2f秒\n' %
                                      (end - start))  # 输出下载用时时间
                    except:
                        input('下载音频出错!\r')
            except Exception as error:
                print("下载错误："+error)

            try:
                fileName=re.sub(r'[\\/:*?"<>|\r\n]+', "_", author_list[i])
                shortFileName=self.dealFileName(fileName)
                v_url = self.save + self.mode + '/' + nickname[i] + '/' + fileName+str(aweme_id[i]) + '.mp4'
                v_url_OLD = self.save + self.mode + '/' + nickname[i] + '/' + fileName + '.mp4'
                v_url_short = self.save + self.mode + '/' + nickname[i] + '/' + shortFileName+str(aweme_id[i]) + '.mp4'
                
                print('')
                print('[视频标题]:'+author_list[i])  # 开始下载，显示下载文件大小

                if os.path.isfile(v_url) or os.path.isfile(v_url_OLD) or os.path.isfile(v_url_short):  # 判断视频是否存在，避免重复下载
                    print('[保存地址]:'+v_url_short)
                    print("[下载结果]:视频已下载，已为你跳过~")
                    if isUpdateFlag == True:
                        return
                    continue
                
                video = requests.get(video_list[i])  # 保存视频
                start = time.time()  # 下载开始时间
                size = 0  # 初始化已下载大小
                chunk_size = 1024  # 每次下载的数据大小
                content_size = int(video.headers['content-length'])  # 下载文件总大小
                try:
                    if video.status_code == 200:  # 判断是否响应成功
                        print('[文件大小]:{size:.2f} MB'.format(size=content_size / chunk_size / 1024))
                        print('[保存地址]:'+v_url_short)
                        with open(v_url_short, 'wb') as file:  # 显示进度条
                            for data in video.iter_content(chunk_size=chunk_size):
                                file.write(data)
                                size += len(data)
                                print('\r'+'[下载进度]:%s%.2f%%' % (
                                    '>'*int(size*50 / content_size), float(size / content_size * 100)), end=' ')
                            end = time.time()  # 下载结束时间
                            print('\n' + '[下载结果]:已下载，耗时: %.2f秒\n' %
                                  (end - start))  # 输出下载用时时间
                except Exception as error:
                    print(error)
                    input('下载视频出错!\r')
            except Exception as error:
                print(error)
        self.next_data(max_cursor, userId, isUpdateFlag)


#主模块执行
if __name__ == "__main__":
    RTK = TikTok('')
    sys.exit()
