#_*_coding:utf-8_*_
import socket
import os
import sys
import optparse
import json
import hashlib
import getpass

STATUS_CODE = {
    100:"Invalid command.",
    101:"Data packet was incorrect.",
    202:"Invalid authentication information",
    201:"Username or Password was wrong.",
    200:"OKAY CONFIRMED",
    502:"CMDLine has no <filename> use [help] checking solutions.",
    501:"Target are not in Remote server,use [ls] or [tree] having a look",
    500:"f:Data packing complete.",
    510:"MD5 Passed",
    511:"MD5 unPassed"
}

class FTPClient():
    
    def __init__(self):
        #   自定义数据头文件
        self.header={
        'action':None,      #   行为
        'username':None,    #   用户名
        'password':None,    #   密码
        'f_md5':None,       #   文件的md5验证值
        'f_name':None,      #   文件名
        'f_size':None,      #   文件的长度单位是byte
        'f_type':None,
        'status_code':None,
        'status_msg':None
        }
        
        USAGE = "FTP_Client+++produce by Ray<aka>Heisenberg".center(60,'*')
        self.parser = optparse.OptionParser(usage=USAGE)
        self.parser.add_option("-s","--server",dest='server',help="FTP server ip")
        self.parser.add_option("-p","--port",type="int",dest="port",help="FTP server port")
        self.parser.add_option("-u","--username",dest="username",help="username")
        
        self.login()    #   接收到数据，准备让用户输入密码
        self.verify_args()  #   本地确认输入信息是否有问题
        self.make_connect() #   尝试性的建立一个连接

    def login(self):
        self.option,self.args=self.parser.parse_args()
        self._username = self.option.username
        self._server = self.option.server
        self._port = self.option.port
        if self._username == None:
            self._username = input("Plz type in your ID:")
        self._password = getpass.getpass(f"Plz input [{self._username}]\' password:")
        print(self._password)
        
    #   远程连接
    def make_connect(self):
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

    def authentication(self):
        #   远程服务器判断 用户 密码 action
        self.header['action'] = "auth"
        self.header['username'] = self._username
        self.header['password'] = self._password
        #   发送信息
        self.sock.send(json.dumps(self.header).center(1024,' ').encode())    #   发送到服务器，等待远程服务器响应
        #   -----waiting-----
        response = self.get_response()  #   获取服务器的返回代码
        if response.get('status_code') == 200:  #   通过验证
            print("Passed Authentication".center(60,""))
            return True
        else:
            print(response.get("status_code"))
    #   得到服务器的回复，公共方法。
    def get_response(self):
        data = self.sock.recv(1024).strip()
        data = json.loads(data.decode())
        return data
    #   交互程序
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
                else:
                    print("[{}]--> Invalid Command.".format(self._username.strip()))
                    
    #   MD5
    def _md5_required(self,cmd_list):
        if '--md5' in cmd_list:
            return True
    #   进度条  生成器表示
    def show_progress(self,total):
        received_size = 0
        current_percent = 0
        while received_size:
            if int((received_size/ total) * 100) > current_percent:
                print("*",end='',flush=True)
                current_percent = (received_size/total) * 100
            new_size = yield
            received_size += new_size
    #   get 下载方法
    def _get(self,cmd_list):
        print('get--',cmd_list)
        if len(cmd_list)==1:
            print("No filename follows...")
            return
        #   客户端操作信息
        data_header={
            'action':'get',
            'filename':cmd_list[1]
        }
        
        if self._md5_required(cmd_list):#   命令请求中带有--md5
            data_header['md5'] = True # 向客户端写入MD5请求
            
        self.sock.send(json.dumps(data_header).encode())    #   向客户端发送客户端的操作信息
        response = self.get_response()  #   接受服务器端信息
        print(response)
        
        if response["status_code"] == 257:  #   传输中
            self.sock.send('1'.encode())    #   向服务器发送确认信息
            base_filename = cmd_list[1].split('/')[-1] #    提取文件名
            received_size = 0   #   本地的接受量
            file_obj = open(base_filename,'wb')     #   二进制模式写入
            
            if self._md5_required(cmd_list):   
                md5_obj = hashlib.md5()
                progress = self.show_progress(response['file_size'])
                progress.__next__()
                
                while received_size < response['file_size']:       #    当接受量，小于文件大小，持续循环
                    
                    data = self.sock.recv[4096] #   4Mb
                    received_size += len(data)
                    
                    try:
                        progress.send(len(data))
                    except:
                        print("100%")
                        file_obj.close()
                    
                    file_obj.write(data)    #   把接收的数据写入文件
                    md5_obj.update(data)    #   把数据进行md5加密
                else:   #   对应的上面的while
                    print("--->file recv done<---") #   接收成功
                    file_obj.close()
                    md5_val =md5_obj.digest()
                    md5_from_server = self.get_response()   #   获得服务器md5数据
                    if md5_from_server['status_code'] == 258:
                        print(f"{base_filename}MD5校验一致。")
                        print("服务器效验数据：",md5_from_server)
                        print("本地效验数据：",md5_val)
            else:
                progress = self.show_progress(response['file_size'])
                progress.__next__()
                
                while received_size < response['file-size']:
                    
                    data = self.sock.recv(4096)
                    received_size += len(data)
                    file_obj.write(data)
                    try:
                        progress.send(len(data))
                    except:
                        print('100%')
                else:
                    print("--->file recv done<---")
                    file_obj.close()
    #   put 发送方法
    def _put(self,cmd_list):
        print("put--",cmd_list)
        if len(cmd_list) == 1:
            print("No filename follows...")
            return 
        self.sock.send(json.dumps(data_header).encode())    #   发送客户端的操作信息
        self.sock.recv(1)
        file_obj = open(cmd_list[1],'rb')
        for line in file_obj:
            self.sock.send(line)
    #   填充json头文件
    def fill_header(self):
        self.header['action'] = self.option.username
    #   关闭连接
    def logout(self):
        print(f"账号{self.username}注销".center(60,"*"))
        self.sock.close()
        
        
if __name__ == '__main__':
    ftp = FTPClient()
    ftp.interaction()
                
                