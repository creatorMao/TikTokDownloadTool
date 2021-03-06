import requests
import json
import os
import time
import configparser
import re
import sys
import datetime
import DBService
from urllib import parse

class TikTok():
    #初始化
    def __init__(self,downloadType,homePageUrl):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36 Edg/87.0.664.66'
        }
        
        #self.dbService=DBService.DBService()

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
        self.root_dir= os.path.abspath(os.path.dirname(__file__))

        #实例化读取配置文件
        self.cf = configparser.ConfigParser()

        #用utf-8防止出错
        self.cf.read(self.root_dir+"/conf.ini", encoding="utf-8")

        #读取保存路径
        self.save = self.root_dir+self.cf.get("save", "url")

        #读取下载视频个数
        self.count = int(self.cf.get("count", "count"))

        #读取用户主页地址
        self.userInput = downloadType if downloadType!='' else input('请选择一种功能(输入功能的序号):')

        #读取下载模式
        self.mode = self.cf.get("mode", "mode")

        #保存用户名
        self.nickname = ""

        #用户主页地址前缀
        self.userHomePagePrefix = self.cf.get("api", "userHomePagePrefix")

        #用户主页地址样例
        self.userHomePageExmple = self.cf.get("api", "userHomePageExmple")

        #本次视频下载数量
        self.videoCount=0
        #本次图片下载数量
        self.photoCount=0
        #本次增量下载时，耗时,单位秒
        self.downloadTimeCost=0

        #增量更新用户列表
        hisIncrementalUpdateUserList=self.cf.get("url", "incrementalUpdateUserList")
        self.incrementalUpdateUserList = [] if hisIncrementalUpdateUserList=="" else hisIncrementalUpdateUserList.split(',')

        if self.userInput == '1':
            self.uid = homePageUrl if homePageUrl!='' else self.filterDoubleByteCharacter(input(
                '请输入完整的个人主页地址(例如'+self.userHomePageExmple+'):'))
            
            print(self.uid) 

            if self.uid=="":
                print("你在干什么,地址不能为空的哦！")
                return

            self.end = False
            linkFlag=self.judge_link((self.userHomePagePrefix+self.uid), False)

            if linkFlag==False:
                print("输入的地址不正确")
                return

            print('')
            self.printDownloadCount() 

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

            downloadStart=time.time()
            print('本次增量更新总共有'+str(updateLength)+"个用户")
            for idx in range(updateLength):
                print("")
                print("[下载队列]:正在更新第"+str(idx+1)+"个用户")
                self.end = False
                try:
                    self.judge_link((self.userHomePagePrefix+self.incrementalUpdateUserList[idx]), True)
                except Exception as error:
                    print('[错误原因]:'+error)
                    pass
                
            
            print("")
            self.printDownloadCount()
            downloadEnd=time.time()
            self.downloadTimeCost=(datetime.datetime.fromtimestamp(downloadEnd)-datetime.datetime.fromtimestamp(downloadStart)).seconds
            print('[总耗时]:'+str(self.downloadTimeCost)+"秒！")
            #self.dbService.addDownloadHistory(self.userInput,'1',self.downloadTimeCost,'success',self.videoCount,self.photoCount)
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
        
        index = 0
        successFlag=False
        key=''

        # 最大尝试四次
        while index <= 4 and successFlag==False:
            index+=1

            if index>1:
                print('正在尝试第'+str(index)+'次获取用户主页！')

            #获取解码后原地址
            r=self.requestDeal(self.Find(userId)[0])
            params = parse.parse_qs(parse.urlparse(r.url).query)
            key= params['sec_uid'][0]

            if key:
                successFlag=True

        if successFlag==False:
            return successFlag

        #第一次访问页码
        max_cursor = 0

        #构造第一次访问链接
        api_post_url = 'https://www.iesdouyin.com/web/api/v2/aweme/%s/?sec_uid=%s&count=%s&max_cursor=%s&aid=1128&_signature=PDHVOQAAXMfFyj02QEpGaDwx1S&dytk=' % (
            self.mode, key, str(self.count), max_cursor)
        self.get_data(api_post_url, max_cursor, userId, isUpdateFlag,key)
        return api_post_url, max_cursor, key

    #获取第一次api数据
    def get_data(self, api_post_url, max_cursor, userId, isUpdateFlag,key):
        #尝试次数
        index = 0
        #存储api数据
        result = []
        
        while result == [] and index <= 4 and self.end==False:
            index += 1

            if index>=5:
                print('[抓取日志]:第1页，抓取次数超过最大次数，即将为您跳过~骚瑞(sorry)~')

            print('')
            print('[抓取日志]:正在对第1页，进行第 %d 次抓取\r' % index)
            response=self.requestDeal(api_post_url)
            html = json.loads(response.content.decode())

            if 'max_cursor' in html.keys():
                max_cursor = html['max_cursor']

            # 先判断第一次接口是否正常，api经常抽风，获取不到aweme_list和max_cursor，判断5次，不行就彻底跳过
            if 'aweme_list' in html.keys() and len(html['aweme_list']) > 0:
                print('[抓取日志]:第1页，第 %d 次抓取成功！\r' % index)

                if self.end == False:
                    #下一页值
                    self.nickname = html['aweme_list'][0]['author']['nickname']
                    print('[用户名称]:'+str(self.nickname)+'\r')
                    
                    result = html['aweme_list']

                    #处理第一页视频信息
                    self.video_info(result, max_cursor, userId, isUpdateFlag,key)
                else:
                    self.next_data(max_cursor, userId, isUpdateFlag,key)
            else:
                print('[抓取日志]:第1页，无数据。')
                self.next_data(max_cursor, userId, isUpdateFlag,key)

        return result, max_cursor

    #下一页
    def next_data(self, max_cursor, userId, isUpdateFlag,key):

        #构造下一次访问链接
        api_naxt_post_url = 'https://www.iesdouyin.com/web/api/v2/aweme/%s/?sec_uid=%s&count=%s&max_cursor=%s&aid=1128&_signature=RuMN1wAAJu7w0.6HdIeO2EbjDc&dytk=' % (
            self.mode, key, str(self.count), max_cursor)
        index = 0
        result = []
        while self.end == False:

            #回到首页，获取抓取次数超过5次，则结束
            if max_cursor == 0  or index >= 4:
                if max_cursor==0:
                    print('[抓取日志]:当前是该用户的最后一页，即将为您跳过~')
                
                if index>=4:
                    print('[抓取日志]:抓取次数超过最大次数，已跳过~骚瑞(sorry)~')

                self.end = True
                return

            index += 1
            
            print('')
            print('[抓取日志]:正在对', max_cursor, '页,进行第',index,'次抓取')
            
            response=self.requestDeal(api_naxt_post_url)
            html = json.loads(response.content.decode())

            if self.end == False and 'max_cursor' in html.keys():
                #下一页值
                max_cursor = html['max_cursor']
                result = html['aweme_list']
                print('[抓取日志]:', max_cursor, '页抓取成功')

                if len(result)==0:
                    print('[抓取日志]:', max_cursor, '页无数据。')

                #处理下一页视频信息
                self.video_info(result, max_cursor, userId, isUpdateFlag,key)
            else:
                self.end == True
                print('[抓取日志]:', max_cursor, '页抓获数据失败')
    
    #过滤掉双字节字符
    def filterDoubleByteCharacter(self,text):
        return re.sub("[^\x00-\xff]", '', text).replace(' ','')

    #打印本次下载统计
    def printDownloadCount(self):
        mode="全量"
        if self.userInput=="2":
            mode="增量"
        print(mode+"下载已完成!本次共下载"+str(self.videoCount)+"个视频,"+str(self.photoCount)+"张照片！")
        pass

    def requestDeal(self,url):
        i = 0
        while i < 3:
            try:
                time.sleep(0.5)
                return  requests.get(url, timeout=5,headers=self.headers)
            except requests.exceptions.RequestException:
                print(url)
                print("[请求超时]:第"+str(i+1)+"次请求超时！即将进行第"+str(i+2)+"次尝试！")
                i += 1

    def download(self,type,title,saveUrlList,orignUrl):
        typeName="文件";
        if type=="mp4":
            typeName="视频"
        if type=="jpeg":
            typeName="图片"

        print('')
        print('['+typeName+'标题]:'+title)

        #判断视频是否存在，避免重复下载
        for i in range(len(saveUrlList)):
            if os.path.isfile(saveUrlList[i]):  
                print('[保存地址]:'+saveUrlList[i])
                print("[下载结果]:视频已经下载过，已为你跳过~")
                return True

        video = self.requestDeal(orignUrl)# 保存视频
        start = time.time()  # 下载开始时间
        size = 0  # 初始化已下载大小
        chunk_size = 1024  # 每次下载的数据大小
        content_size = int(video.headers['content-length'])  # 下载文件总大小
        try:
            if video.status_code == 200:  # 判断是否响应成功
                print('['+typeName+'大小]:{size:.2f} MB'.format(
                    size=content_size / chunk_size / 1024))
                print('[保存地址]:'+saveUrlList[0])
                with open(saveUrlList[0], 'wb') as file:  # 显示进度条
                    for data in video.iter_content(chunk_size=chunk_size):
                        file.write(data)
                        size += len(data)
                        print('\r'+'[下载进度]:%s%.2f%%' % ('>'*int(size*50 / content_size), float(size / content_size * 100)), end=' ')
                    end = time.time()  # 下载结束时间
                    print('\n' + '[下载结果]:下载成功！耗时: %.2f秒\n' % (end - start))  # 输出下载用时时间
                    return False
        except Exception as error:
            print('[下载结果]:下载'+typeName+'出错!')
            print('[错误原因]:'+error)
            return False

    #处理视频信息
    def video_info(self, result, max_cursor, userId, isUpdateFlag,key):
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
                    alreadyExistFlag=self.photos_download(title, id, nick)
                    if alreadyExistFlag==True and isUpdateFlag == True:
                        break
                    continue

            except Exception as error:
                print(error)
                pass

        self.videos_download(author_list, video_list, aweme_id,
                             nickname, max_cursor, userId, isUpdateFlag,key)

        return self, author_list, video_list, aweme_id, nickname, max_cursor
    
    # 处理文件名称，如果太长则截取，只取50个字
    def dealFileName(self,name):
        if len(name)>=50:
            return name[0:50]
        return name

    #图片下载
    def photos_download(self, author_name, id, nickname):
        try:
            #创建并检测下载目录是否存在
            os.makedirs(self.save + self.mode + '/' + nickname)
        except:
            #有目录不再创建
            pass
        try:
            # 官方接口
            jx_url = f'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={str(id)}'
            js = json.loads(self.requestDeal(jx_url).text)
            images = js['item_list'][0]['images']
            
            alreadyExistFlag=True
            for i in range(len(images)):
                imagesUrl = str(images[i]['url_list'][len(images[i]['url_list'])-1])
                
                name=re.sub(r'[\\/:*?"<>|\r\n]+', "_", author_name)
                photoUrl = self.save + self.mode + '/' + nickname + '/' + name+ str(id)+str(i) + '.jpeg'
                photoShortUrl=self.save + self.mode + '/' + nickname + '/' + self.dealFileName(name)+ str(id)+str(i) + '.jpeg'

                alreadyExistFlag=self.download('jpeg',name,[photoShortUrl,photoUrl],imagesUrl)

                if alreadyExistFlag==False:
                    self.photoCount+=1

            return alreadyExistFlag

        except Exception as error:
            print("图片下载错误："+error)
            return False
            
    def videos_download(self, author_list, video_list, aweme_id, nickname, max_cursor, userId, isUpdateFlag,key):
        for i in range(len(video_list)):
            try:
                #创建并检测下载目录是否存在
                os.makedirs(self.save + self.mode + '/' + nickname[i])
            except:
                #有目录不再创建
                pass

            try:
                fileName=re.sub(r'[\\/:*?"<>|\r\n]+', "_", author_list[i])
                shortFileName=self.dealFileName(fileName)
                v_url = self.save + self.mode + '/' + nickname[i] + '/' + fileName+str(aweme_id[i]) + '.mp4'
                v_url_OLD = self.save + self.mode + '/' + nickname[i] + '/' + fileName + '.mp4'
                v_url_short = self.save + self.mode + '/' + nickname[i] + '/' + shortFileName+str(aweme_id[i]) + '.mp4'
                
                alreadyExistFlag=self.download('mp4',author_list[i],[v_url_short,v_url_OLD,v_url],video_list[i])

                if alreadyExistFlag==False:
                    self.videoCount+=1

                if alreadyExistFlag==True and isUpdateFlag == True:
                    return
                continue

            except Exception as error:
                print(error)
        self.next_data(max_cursor, userId, isUpdateFlag,key)

#主模块执行
if __name__ == "__main__":
    if len(sys.argv)==3:
        RTK = TikTok(sys.argv[1],str(sys.argv[2]))
    elif len(sys.argv)==2:
        RTK = TikTok(sys.argv[1],'')
    else:
        RTK = TikTok('','')
    sys.exit()
