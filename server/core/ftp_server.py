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


class FTPHandler(socketserver.BaseRequestHandler):
    #   服务器进程函数

    def handle(self):
        self._bool_user_auth = 0
        
        while True:
            self.data = self.request.recv(1024).strip()
            if not self.data:
                print('*'*60)
                print("[{}]:断开连接".format(self.client_address[0]))
                print('*'*60)
                self.request.close()
                break
            data = json.loads(self.data.decode())   #   接受信息，并且从json对象转化为字典数据
            if data.get('action') is not None:
                if hasattr(self,"_%s" % data.get('action')):    #   客户端action 符合服务端action
                    if data.get('action') == "auth" or self._bool_user_auth == 1:   # 除了_auth指令之外，如果没有通过认证一律关闭连接
                        print("[{}]--> ${}".format(self.client_address[0],data.get('action')))
                        func = getattr(self,"_%s" % data.get('action'))
                        func(data)
                    else:
                        print("[{}]--> Danger action,kick off [{}].".format(self.client_address[0],self.data.get['username']))
                        self.request.close()
                else:   #   客户端action不正确
                    print("[{}]--> Incorrect cmd.".format(self.client_address[0]))
                    self.send_response(100) #   返回251,无效的cmd格式
            else:   #   客户端action不正确
                print("[{}]--> Empty cmd.".format(self.client_address[0]))
                self.send_response(101) #   250：无效的cmd格式：并且显示提示
    #   向客户端返回数据
    ###############################################################
    def send_response(self,status_code,other_response_header=None):
        response = {'status_code':status_code}
        if other_response_header:
            response.update(other_response_header)
        self.request.sendall(json.dumps(response).encode())
    ###############################################################
    #   核对客户端信息，用户名：密码。
    def _auth(self,*args,**kwargs):
        data = args[0]
        if data.get("username") is None or data.get("password") is None:    #   客户端传来的数据中用户名或者密码有空的
            self.send_response(202) #   验证数据无效    
        else:
            if self.authenticate(data.get("username"),data.get("password")):
                self.send_response(200)
                print("[{}]--> OKAY:set _bool_user_auth = 1".format(self.client_address[0]))
                self._bool_user_auth = 1
            else:
                self.send_response(201)
                print("[{}]--> Username or Password incorrect".format(self.client_address[0]))
            
    #   校验用户的合法性
    def authenticate(self,username,password):
        config = configparser.ConfigParser()
        config.read(settings.ACCOUNT_FILE)
        if username in config.sections():   #   用户名是否存在
            _password = config[username]["password"]
            if _password == password:   #   密码是否一致
                del(_password)  #   清空无用数据内存
                print(f"welcome {username}".center(60,'*'))  
                return True
            else:
                return False
        else:
            return False

    #   接受客户端传输来的文件，并且保存到服务器。        
    # def _put(self,*args,**kwargs):
    #     data = args[0]
    #     base_target = data.get('filename')
    #     #   abs_path = self.USER_HOME_PATH + os.sep + base_target
    #     print(abs_path)
    #     if os.path.isfile(abs_path):
    #         file_obj = open(abs_path,'wb')
    #         data = self.request.recv(4096)
    #         file_obj.write(data)
    #         file_obj.close()
    # #   
    # def _get(self,*args,**kwargs):
    #     data = args[0]
    #     if data.get("filename") is None:
    #         self.send_response(255) #   255:文件名不存在
    #     #   user_home_dir = "%s/%s" %(settings.USER_HOME,self.user['filename']) #   当前连接用户的目录
    #    #     file_abs_path = "%s/%s" %(user_home_dir,data.get('filename'))   #   文件的绝对路径
        
    #     print("file \'s abs path :",file_abs_path)
        
    #     if os.path.isfile(file_abs_path):
    #         file_obj = open(file_abs_path,'rb') #   使用Byte打开文件
    #         file_size = os.path.getsize(file_abs_path)  #   读取文件长度 
    #         #   self.send_response(257,data={'file_size':file_size})    #   返回即将传输的文件的大小
            
    #         self.request.recv(1)    #   等待客户端确认
            
    #         if data.get('md5'): #   有 --md5 则传输时候加上加密
    #             md5_obj = hashlib.md5()
    #             for line in file_obj:
    #                 self.request.send(line)
    #                 md5_obj.update(line)
    #             else:
    #                 file_obj.close()
    #                 md5_val = md5_obj.hexdigest()
    #                 self.send_response(258,{'md5':md5_val})
    #                 print("Sending file done...")
    #         else:   #   没有 md5 直接传输文件
    #             for line in file_obj:
    #                 self.request.send(line)
    #             else:
    #                 file_obj.close()
    #                 print("Sending file done...")
    #     else:   
    #         self.send_response(256)     #   256:服务器上面不存在该文件
    # def get_file_tree(self,path):
    #     pass
    # def ls(self,*args,**kwargs):
    #     eval(os.system(args[0]))
    
if __name__ == '__main__':
    print("going to start server".center(60,'#'))
    server = socketserver.ThreadingTCPServer((settings.HOST,settings.PORT),FTPHandler)
    server.serve_forever()