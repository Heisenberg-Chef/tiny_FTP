#_*_coding:utf-8_*_
import socket
import os
import sys
import optparse
import json
import hashlib
import getpass
import time
BASE_CACHE = os.path.abspath(os.path.dirname(__file__))

STATUS_CODE = {
    100:"Invalid command.",
    101:"Data packet was incorrect.",
    202:"Invalid authentication information",
    201:"Username or Password was wrong.",
    200:"OKAY CONFIRMED",
    502:"Geting process is finished.",
    501:"Target are not in Remote server,use [tree] having a look",
    500:"File checking progressing complete.",
    510:"MD5 Passed",
    511:"MD5 unPassed",
    404:"Fatal Error : I don\'t know..."
}

class FTPClient():
    
    def __init__(self):
        #   自定义数据头文件
        self.header={       
            'action':None,      #   行为
            'username':None,    #   用户名
            'password':None,    #   密码
            'f_md5':False,      #   文件的md5验证值
            'f_name':None,      #   文件名
            'f_size':None,      #   文件的长度单位是byte
            'abs_path':None,    #   文件在本机的绝对路径
            'rel_path':None     #   文件相对于家目录路径
            }
        self.pack_size = 512
        USAGE = "FTP_Client+++produce by Ray<aka>Heisenberg".center(60,'*') + '\nIf you are new user,please sign up before login\n \
            use function {-c} or {--create} '
        self.md5_opt = False
        self.parser = optparse.OptionParser(usage=USAGE)
        self.parser.add_option("-s","--server",dest='server',help="FTP server ip")
        self.parser.add_option("-p","--port",type="int",dest="port",help="FTP server port")
        self.parser.add_option("-u","--username",dest="username",help="User\'s name.")
        #   并不存储变量
        self.parser.add_option("-c","--create",dest="c_flag",action="store_false",help="Sign up an Account for user.",default = None)
        #   if self.option.c_flag != None:  #   使用c_flag注册
            
        self.option,self.args=self.parser.parse_args()  #   分析命令行中传入的参数        
        self.host_check()   #   host:port检查
        self.login()    #   接收到数据，准备让用户输入密码
        self.verify_args()  #   本地确认输入信息是否有问题
        self.make_connect() #   尝试性的建立一个连接
        
    #   def sign_up(self)：     #   保留注册功能

    def host_check(self):
        if self.option.server == None or self.option.port == None:
            self._server = str(input("[Client]: Server\'s IP--> "))
            self._port = int(input("[Client]: Server\'s PORT--> "))
        else:
            self._server = self.option.server
            self._port = self.option.port

    def login(self):    #   封装登陆信息，在登陆之前
        self._username = self.option.username
        if self._username == None:
            self._username = input("[Client]: ID--> ")
        self._password = getpass.getpass(f"[Client]: [{self._username}]\'s password--> ")
        
    #   远程连接
    def make_connect(self):     #   建立一个连接
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.connect((self._server,self._port))

    #   效验合法性
    def verify_args(self):  
        if self._username is not None and self._password is not None:
            pass    #   用户名，密码都不是空
        else:   #   二者有一个是空的
            sys.exit("User\'s authentication information was empty.")            
        if self._server and self._port:
            #  检查端口是否完整
            if self._port > 0 and self._port < 65535:
                return True
            else:
                sys.exit("Port must be limited between 0 to 65535 [U can ask administator for actucal port number]")

    def authentication(self):   #   认证
        #   远程服务器判断 用户 密码 action
        self.header['action'] = "auth"
        self.header['username'] = self._username
        self.header['password'] = self._password
        #   发送信息
        self.sock.send(json.dumps(self.header).center(1024,' ').encode())    #   发送到服务器，等待远程服务器响应
        #   -----waiting-----
        response = self.get_response()  #   获取服务器的返回代码
        if response.get('status_code') == 200:  #   通过验证
            print("Passed Authentication".center(60,"*"))
            return True
        else:
            print(response.get("status_code"),STATUS_CODE[response.get("status_code")])

    def get_response(self):      #   得到服务器的回复，公共方法。
        data = self.sock.recv(1024).strip()
        data = json.loads(data.decode())
        return data

    #   MD5
    def _md5_required(self,cmd_list):
        if '--md5' in cmd_list:
            return True
    #   进度条  生成器表示

    #   get 下载方法
    def _fetch(self,cmd_list):
        '''
        从服务器下载功能函数
        私有函数只能内部调用
        命令行使用get <remote file>进行调用
        '''
        if len(cmd_list) == 1:
            print("[{}]: <get> need at least a filename at Remote server.".format(self._username.strip()))
            return
        #   指令行中删除命令操作符
        try:
            cmd_list.remove('fetch')
        except:
            pass
        if '--md5' in cmd_list:
            self.md5_opt = True
            cmd_list.remove('--md5')
        for target in cmd_list: #   此处target是远程服务器上面相对于家目录的地址，传参时候我就使用了f_name参数进行传输
            self._fill_header(action='get',filename=target,md5_opt=self.md5_opt)
            self.sock.send(json.dumps(self.header).center(1024,' ').encode())
            response = self.get_response()
            while response.get('status_code') == 500:
                #   print(666666)    #   执行函数
                data = json.loads(self.sock.recv(1024).decode().strip())
                print('####################')
                print('####################')
                print(data)
                print(response)
                print('####################')
                print('####################')
                f_name = data.get('f_name')
                remanent = data.get('f_size')
                rel = data.get('rel_path')
                f_abs = BASE_CACHE
                for i in rel:
                    f_abs = os.path.join(f_abs,i)
                    if os.path.exists(f_abs) or i == f_name:
                        pass
                    else:
                        os.mkdir(f_abs)
                f_abs = os.path.join(f_abs,f_name)  #   本地绝对路径封装完毕
                
                f = open(f_abs,'wb')
                self.sock.send(str(self.pack_size).center(64,' ').encode())
                while remanent > 0:
                    if remanent > self.pack_size:
                        temp = self.sock.recv(self.pack_size)
                        f.write(temp)
                        remanent -= self.pack_size
                    else:
                        temp = self.sock.recv(remanent)
                        f.write(temp)
                        remanent -= remanent
                print('-'*60)
                response = self.get_response()

                print(response)
            if response.get('status_code') == 501:
                print(response.get('status_code'),STATUS_CODE[response.get("status_code")])
            elif response.get('status_code') == 502:
                print(response.get('status_code'),STATUS_CODE[response.get("status_code")])
            else:
                return
            
            
        
        
    #   put 发送方法
    def _push(self,cmd_list,recursion=None,):
        '''
        _put为私有函数，功能：上传
        recursion是递归操作选项，不要对他进行传参。
        函数使用默认的分析，递归操作
        '''
        try:
            cmd_list.remove('push')
        except:
            pass
        if recursion == None:
            if len(cmd_list) == 0:  #   初步判定put是否正确
                print("[{}]: No filename follows...".format(self._username.strip()))
            if '--md5' in cmd_list:
                self.md5_opt = True
                cmd_list.remove('--md5')
            else:
                self.md5_opt = False
            self.header['f_md5'] = self.md5_opt
            for target in cmd_list:
                thePath = os.path.join(BASE_CACHE,target)   #   包括文件/目录的绝对路径
                relPath = os.path.dirname(os.path.relpath(thePath,BASE_CACHE))  #   相对于工作目录的计算出来的路径
                if os.path.isfile(thePath):
                    recursion = None
                    self._fill_header(action="push",filename = target,md5_opt = self.md5_opt,\
                        abs_path = thePath,relative_path = relPath) #   疯狂传参就对了
                    print(self.header)
                    ######################################
                    #   在这里写网络通信
                    #<!--></-->
                    self.sock.sendall(json.dumps(self.header).center(1024,' ').encode()) # 发送文件头信息
                    # #   等待服务器响应封包数据的尺寸，默认512一个包
                    package_size = int(self.sock.recv(64).decode().strip())

                    f = open(thePath,'rb')
                    file_size = self.header.get('f_size')
                    remanent = file_size
                    #   开始传输
                    while remanent > 0:
                        if remanent < package_size:
                            self.sock.send(f.read(remanent))
                        else:
                            self.sock.send(f.read(package_size))
                        remanent -= package_size
                        #   进度条
                    #   传输完毕关闭句柄
                    f.close()
                    print("-"*60)
                elif os.path.isdir(thePath):
                    cmd_list = os.listdir(thePath)
                    self._push(cmd_list,recursion=thePath)
                else:
                    print("[{}]: <{}> does not exist.".format(self._username.strip(),target))
        else:
            for target in cmd_list:
                thePath = os.path.join(recursion,target)                        #   包括文件/目录的绝对路径
                relPath = os.path.dirname(os.path.relpath(thePath,BASE_CACHE))  #   相对于工作目录的计算出来的路径
                if os.path.isfile(thePath):
                    
                    dir_list = []
                    while relPath != '':
                        dir_list.append(os.path.basename(relPath))
                        #   print(dir_list)
                        relPath = os.path.dirname(relPath)
                    dir_list.reverse()
                    self._fill_header(action="push",filename = target,md5_opt = self.md5_opt,\
                        abs_path = thePath,relative_path = dir_list)             #   疯狂传参就对了
                    ######################################
                    #   在这里写网络通信
                    #<!--></-->
                    self.sock.sendall(json.dumps(self.header).center(1024,' ').encode()) # 发送文件头信息
                    # #   等待服务器响应封包数据的尺寸，默认512一个包
                    package_size = int(self.sock.recv(64).decode().strip())

                    f = open(thePath,'rb')
                    file_size = self.header.get('f_size')
                    remanent = file_size
                    #   开始传输
                    while remanent > 0:
                        if remanent < package_size:
                            self.sock.send(f.read(remanent))
                        else:
                            self.sock.send(f.read(package_size))
                        remanent -= package_size
                        #   进度条
                    #   传输完毕，关闭句柄
                    f.close()   
                    print("-"*60)
                else:
                    thePath = os.path.join(recursion,target)
                    cmd_list = os.listdir(thePath)
                    self._push(cmd_list,thePath)
                    
                    

    #   填充json头文件
    def _fill_header(self,action,filename,md5_opt,abs_path=None,relative_path=None):
        self.header['action'] = action
        self.header['username'] = self.option.username
        self.header['password'] = self._password
        self.header['f_name'] = filename
        self.header['f_md5'] = md5_opt
        if action == 'push':
            self.header['f_size'] = os.stat(abs_path).st_size
        else:
            self.header['f_size'] = None
        self.header['rel_path'] = relative_path
        self.header['abs_path'] = abs_path
        
    #   关闭连接
    def _logout(self,cmd_list):
        print(f"Account {self._username} is logging out.".center(60,"*"))
        self.sock.close()
        sys.exit("Thx for using!!\nIf U like my tiny_FTP,plz give a star. :)")
################################################## 交互程序  ############################################
    def interaction(self):
        if self.authentication():   #   认证成功
            print("Starting interactive with remote server".center(60,"*"))
            while True:
                cmd = input("[%s]:" % (self._username.strip()))
                if len(cmd) == 0:
                    continue # ;
                cmd_list = cmd.strip().split()
                if hasattr(self,"_{}".format(cmd_list[0])):
                    func = getattr(self,"_{}".format(cmd_list[0]))
                    func(cmd_list)  #   执行方法
                elif cmd_list[0] in ['exit','quit','exit'.upper(),'quit'.upper(),'q','Q']:
                    self._logout(cmd_list)
                else:
                    print("[{}]: Invalid Command.".format(self._username.strip()))
                    
########################################################################################################
if __name__ == '__main__':
    ftp = FTPClient()
    ftp.interaction()

                