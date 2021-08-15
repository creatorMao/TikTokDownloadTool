import sys
import TikTokMulti

#主模块执行
if __name__ == "__main__":
    # 自动下载脚本

    if len(sys.argv)<2:
        print('参数不正确')
    RTK = TikTokMulti.TikTok('1',str(sys.argv[1]))
    sys.exit()
