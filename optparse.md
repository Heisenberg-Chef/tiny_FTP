# import optparse

# parser = optparse.OptionParser()

# parser.add_option('-f','--file',action = 'store',type = 'string',dest = 'filename')
# parser.add_option('-v','--verbose',action = 'store_false',dest="verbose",default = 'hello',help=\
#     "make lots of noise [default]")

# #   parser.parse_args() 解析并且返回一个字典和列表
# #   字典中的关键字是我们所有的add_option()函数中的dest参数值
# #   而对应的Value，是add_option()函数中的default
# #   或者是用户传入的parse.parse_args()参数

# fakeArgs = ['-f','file.txt','-v','how are you','arg1','arg2']
# option,args = parser.parse_args()
# op , ar = parser.parse_args(fakeArgs)
# print("option:",option)
# print("args:",args)
# print("op:",op)
# print("ar:",ar)


import optparse
usage="python %prog -H <target host> -p/-P <target ports>"  #用于显示帮助信息
parser=optparse.OptionParser(usage)  #创建对象实例
parser.add_option('-H',dest='Host',type='string',help='target host')   ##需要的命令行参数
parser.add_option('-P','-p',dest='Ports',type='string',help='target ports',default="20,21")  ## -p/-P 都可以
options,args=parser.parse_args()
print(options.Host)
print(options.Ports)
