import os
import sys
import time
import calendar
def dfs_show(path,depth):
    
    if depth == 0:
        print("#"*60)
        print("#        服务器系统信息：",sys.platform)
        print("#        目前的本地时间：",time.strftime("%Y年%m月%d日：%H:%M:%S"))
        print("#        深度优先索引，+是文件夹，#为文件")
        print("#"*60)
        print("root:[{}]".format(path))
    for i in os.listdir(path):
        if os.path.isdir(os.path.abspath(os.path.join(path,i))) and i != '.git':
            print('|············'* depth + '+--'+i)
            dfs_show(os.path.abspath(os.path.join(path,i)),depth+1)
        else:
            # print(f"{i} is file")
            print('|············'*depth+'#--',i)

dfs_show('.',0)

