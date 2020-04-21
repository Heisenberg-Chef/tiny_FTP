#_*_coding:utf-8_*_

import socketserver
import json
import configparser
import os
import hashlib
import sys


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)   #   向我们的索引库目录中加入BASE_DIR

from conf import settings
from core import main 

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

class FTPHandler(socketserver.BaseRequestHandler):
    #   服务器进程函数
    def handle(self):
        while True:
            self.data = self.request.recv(1024).strip()
            #   print(self.client_address[0])
            print(self.data)
            # self.request.sendall(self.data.upper())

            if not self.data:
                print("client closed...")
                break

            data = json.loads(self.data.decode())   #   接受客户端的信息并且转化为json对象
            
            if data.get('action') is not None:
                
                if hasattr(self,"_%s" % data.get('action')):    #   客户端action 符合服务端action
                    print("--get in auth-->",hasattr(self,"_{}".format(data.get('action'))))
                    func = getattr(self,"_%s" % data.get('action'))
                    print(func)
                    print(data)
                    func(data)
                else:   #   客户端action不正确
                    print("Invalid cmd format.")
                    self.send_response(251) #   返回251,无效的cmd格式
            else:   #   客户端action不正确
                print("Invalid cmd format")
                self.send_response(250) #   250：无效的cmd格式：并且显示提示
    #   向客户端返回数据
    def send_response(self,status_code,data=None):
        response = {'status_code':status_code,'status_msg':STATUS_CODE[status_code]}
        if data:
            response.update(data)
        self.request.send(json.dumps(response).encode())
        
    #   核对客户端信息，用户名：密码。
    def _auth(self,*args,**kwargs):
        data = args[0]
        print("in _auth:",data)
        if data.get("username") is None or data.get("password") is None:    #   客户端传来的数据中用户名或者密码有空的
            self.send_response(252) #   验证数据无效    
        user = self.authenticate(data.get("username"),data.get("password")) #   把客户端的用户密码进行校验
        if user is None:    #   客户端数据为空，返回错误
            self.send_response(253)     #   253：错误的用户名或密码
        else:
            print("Passing authentication:",user)
            self.user = user
            self.send_response(254) #   254:通过身份验证          
            
    #   校验用户的合法性
    def authenticate(self,username,password):
        print("get in authentication",username,password)
        config = configparser.ConfigParser()
        config.read(settings.ACCOUNT_FILE)
        if username in config.sections():    #   匹配成功了
            print("ok sections")
            _password = config[username]["password"]
            if _password == password:
                print("pass authentication.",username)
                return config[username]

    #   接受客户端传输来的文件，并且保存到服务器。        
    def _put(self,*args,**kwargs):
        data = args[0]
        base_filename = data.get('filename')
        file_obj = open(base_filename,'wb')
        data = self.request.recv(4096)
        file_obj.write(data)
        file_obj.close()
    #   
    def _get(self,*args,**kwargs):
        data = args[0]
        if data.get("filename") is None:
            self.send_response(255) #   255:文件名不存在
        user_home_dir = "%s/%s" %(settings.USER_HOME,self.user['filename']) #   当前连接用户的目录
        file_abs_path = "%s/%s" %(user_home_dir,data.get('filename'))   #   文件的绝对路径
        
        print("file \'s abs path :",file_abs_path)
        
        if os.path.isfile(file_abs_path):
            file_obj = open(file_abs_path,'rb') #   使用Byte打开文件
            file_size = os.path.getsize(file_abs_path)  #   读取文件长度 
            self.send_response(257,data={'file_size':file_size})    #   返回即将传输的文件的大小
            
            self.request.recv(1)    #   等待客户端确认
            
            if data.get('md5'): #   有 --md5 则传输时候加上加密
                md5_obj = hashlib.md5()
                for line in file_obj:
                    self.request.send(line)
                    md5_obj.update(line)
                else:
                    file_obj.close()
                    md5_val = md5_obj.hexdigest()
                    self.send_response(258,{'md5':md5_val})
                    print("Sending file done...")
            else:   #   没有 md5 直接传输文件
                for line in file_obj:
                    self.request.send(line)
                else:
                    file_obj.close()
                    print("Sending file done...")
        else:   
            self.send_response(256)     #   256:服务器上面不存在该文件
            
    def ls(self,*args,**kwargs):
        eval(os.system(args[0]))
    
if __name__ == '__main__':
    server = main.ArvgHandler()
    server.start()