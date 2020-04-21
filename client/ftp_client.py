#_*_coding:utf-8_*_
import socket
import os
import sys
import optparse
import json
import hashlib

STATUS_CODE = {
    250:"Invalid cmd format,e.g:{'action':'get','filename':'test.py','size':344}",
    251:"Invalid cmd",
    252:"Invalid auth data",
    253:"Wrong username or password",
    254:"Passed authentication",
    255:"filename doesn't provided",
    256:"File doesn't exist on server",
    257:"ready to send file",
    258:"md5 verification",
}

class FTPClient():
    def __init__(self):
        parser = optparse.OptionParser()
        parser.add_option("-s","--server",dest='server',help="ftp server ip_addr")
        parser.add_option("-p","--port",type="int",dest="port",help="ftp server port")
        parser.add_option("-u","--username",dest="username",help="user \' ID.")
        parser.add_option("-c","--password",dest="password",help="authentication about password.")
        
        self.option,self.args=parser.parse_args()
        self.verify_args()
        self.make_connect()
    #   远程连接
    def make_connect(self):
        self.sock = socket.socket()
        self.sock.connect((self.option.server,self.option.port))
    #   效验合法性
    def verify_args(self):
        if self.option.username is not None and self.option.password is not None:
            pass    #   用户名，密码都不是空
        else:
            #   二者有一个是空的
            sys.exit("Err:username and password must be provided.")
            
        if self.option.server and self.option.port:
            #  检查端口是否完整
            if self.option.port > 0 and self.option.port < 65535:
                return True
            else:
                sys.exit("Err:Port must in 0-65535")
    #  获得验证用户信息是否正确：
    def authentication(self):
        if self.option.username:    #   有输入信息 则发到服务器进行判断
            print(f"Sending our logging information to remote server.\n\
                username:{self.option.username}\n\
                    password:{self.option.password}")
            return self.get_auth_result(self.option.username,self.option.password)
        
    def get_auth_result(self,user,passwd):
        #   远程服务器判断 用户 密码 action
        data = {
            'action':'auth',
            'username':user,
            'password':passwd
        }
        #发送信息
        self.sock.send(json.dumps(data).center(1024,' ').encode())    #   发送到服务器，等待远程服务器响应
        #   -----waiting-----
        response = self.get_response()  #   获取服务器的返回代码
        if response.get('status_code') == 254:  #   通过验证
            print("passed authentication.")
            self.user = data.get('username')
            return True
        else:
            print(response.get("status_msg"))
    #   得到服务器的回复，公共方法。
    def get_response(self):
        data = self.sock.recv(1024)
        data = json.loads(data.decode())
        return data
    #   交互程序
    def interaction(self):
        if self.authentication():   #   认证成功
            print("start interative with server.".center(60,"-"))
            while True:
                choice = input("[%s]:"%(self.user.strip()))
                if len(choice) == 0:
                    continue # ;
                cmd_list = choice.strip().split()
                if hasattr(self,"_{}".format(cmd_list[0])):  # 反射判断 方法名是否存在
                    func = getattr(self,"_{}".format(cmd_list[0]))
                    func(cmd_list)  #   执行方法
                else:
                    print("Invalid cmd.")
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
        #   头
        data_header = {
            'action':'put',
            'filename':cmd_list[1]
        }
        self.sock.send(json.dumps(data_header).encode())    #   发送客户端的操作信息
        self.sock.recv(1)
        file_obj = open(cmd_list[1],'rb')
        for line in file_obj:
            self.sock.send(line)
            
if __name__ == '__main__':
    ftp = FTPClient()
    ftp.interaction()
                
                