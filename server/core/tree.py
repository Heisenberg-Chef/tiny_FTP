import os
import sys
def dfs_show(path,depth): 
    tmp = ''
    if depth == 0:
        tmp = tmp + "root:[{}]\n".format(path)
    for i in os.listdir(path):
        if os.path.isdir(os.path.abspath(os.path.join(path,i))) and i != '.git':
            tmp = tmp + '|···'* depth + '+ '+str(i) + '\n'+ dfs_show(os.path.abspath(os.path.join(path,i)),depth+1)
        else:
            # print(f"{i} is file")
           tmp = tmp + '|···'*depth+'# '+str(i)+'\n'
    return tmp
# s = dfs_show('.',0)
# print(s)
# print(len(s))
# print(type(s))