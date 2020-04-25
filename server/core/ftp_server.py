#_*_coding:utf-8_*_

import socketserver
import json
import configparser
import os
import hashlib
import sys
import time
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)   #   向我们的索引库目录中加入BASE_DIR

from conf import settings

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
    404:"Fatal Error : I don\'t know...",
    400:"Single File transmition completed,but target is entire folder."
}


class FTPHandler(socketserver.BaseRequestHandler):
    #   服务器进程函数

    def handle(self):
        self._bool_user_auth = 0
        self._package_length = 512
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
        while True:
            self.data = self.request.recv(1024).strip()
            if not self.data:
                print('*'*60)
                print("[{}]--> Disconnected.".format(self.client_address[0]))
                print('*'*60)
                self.request.close()
                break
            data = json.loads(self.data.decode())   #   接受信息，并且从json对象转化为字典数据
            if data.get('action') is not None:
                if hasattr(self,"_%s" % data.get('action')):    #   客户端action 符合服务端action
                    if data.get('action') == "auth" or self._bool_user_auth == 1:   # 除了_auth指令之外，如果没有通过认证一律关闭连接
                        print("[{}]--> ${}".format(self.client_address[0],data.get('action')))
                        func = getattr(self,"_%s" % data.get('action'))
                        print("In listen # ",data)
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
        global STATUS_CODE
        response = {'status_code':status_code,'status_msg':STATUS_CODE[status_code]}
        if other_response_header:
            response.update(other_response_header)
        self.request.send(json.dumps(response).center(1024,' ').encode())
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
                self.USER_HOME_PATH = os.path.join(settings.USER_HOME,username)
                print(f"welcome {username}".center(60,'*'))
                return True
            else:
                return False
        else:
            return False
#   服务器端的put可以理解为put到用户的根目录中,逻辑层只对文件
    def _push(self,*args,**kwargs):
        #   接受守护程序发过来的数据包
        cli_header = args[0]
        f_name = cli_header.get('f_name')
        f_size = cli_header.get('f_size')
        f_path = cli_header.get('rel_path')
        #   f_md5 = cli_header.get('f_md5')
        ######################################
        #   分析数据结构
        if f_path == '':    #   直接传过来的文件，存储在用户目录下面
            f = open(os.path.join(self.USER_HOME_PATH,f_name),'wb')
            total = f_size
            self.request.send(str(self._package_length).center(64,' ').encode())   #   数据包长度告诉客户端
            print('package len:',self._package_length)
            while total > 0:
                if total < self._package_length:
                    f.write(self.request.recv(total))
                else:
                    #   暂定512bytes方便实验
                    f.write(self.request.recv(self._package_length))
                total -= self._package_length
            f.close()
            print("[{}]--> [{}] transmition completed.".format(self.client_address[0],f_name))
        else:
            #   self.request.sendall(str(self._package_length).center(64,' ').encode())   #   数据包长度告诉客户端
            temp = self.USER_HOME_PATH
            for i in f_path:
                temp = os.path.join(temp,i)
                if os.path.exists(temp):
                    print('exists')
                    continue;
                else:
                    os.mkdir(temp)
            f = open(os.path.join(temp,f_name),'wb')
            total = f_size
            print('f size:',total)
            time.sleep(0.2)
            self.request.send(str(self._package_length).center(64,' ').encode())   #   数据包长度告诉客户端
            while total >= 0:
                if total < self._package_length:
                    f.write(self.request.recv(total))
                else:
                    #   暂定512bytes方便实验
                    f.write(self.request.recv(self._package_length))
                total -= self._package_length
            f.close()
            print("[{}]--> [{}] transmition completed.".format(self.client_address[0],f_name))

    def _fetch(self,*args,**kwargs):
        cli_header = args[0]
        self._get(cli_header)
        self.send_response(502)
    #   底层封装函数 对于文件的完成信号需要使用fetch外包装
    def _get(self,cli_header):  #   单个文件的信号  
        #print("[{}]--> in get \n [{}] \n\ndebug".format(self.client_address[0],args[0]))
        f_name = cli_header.get('f_name')
        #print(f_name)
        f_md5 = cli_header.get("f_md5")
        f_flag = cli_header.get('action')
        # if f_md5:
        #     pass
        # else:
        #     pass
        dir_list = []
        while f_name != '':
            dir_list.append(os.path.basename(f_name))
            if f_name != '/':
                f_name = os.path.dirname(f_name)
        dir_list.reverse()
        print(dir_list)
        f_name = self.USER_HOME_PATH
        for i in dir_list:
            f_name = os.path.join(f_name,i)
        if os.path.exists(f_name):
            if os.path.isfile(f_name):
                self.send_response(500)
                print('----------> sending response...')
                filename = os.path.basename(f_name)
                self._fill_header(action='file',filename=filename,\
                    abs_path=f_name,relative_path=dir_list)
                self.request.send(json.dumps(self.header).center(1024,' ').encode())
                f = open(f_name,'rb')
                self._per_size = int(self.request.recv(64).decode().strip())
                remanent = self.header['f_size']
                while remanent > 0:
                    if remanent > self._per_size:
                        temp = f.read(self._per_size)
                        self.request.send(temp)
                        remanent -= self._per_size
                    else:
                        temp = f.read(remanent)
                        self.request.sendall(temp)
                        remanent -= remanent
                print("[{}]--> [{}] sending completed.".format(self.client_address[0],f_name))
                if f_flag == 'fetch':
                    self.send_response(502)
            elif os.path.isdir(f_name):
                tmp_list = os.listdir(f_name)
                try:
                    tmp_list.remove('.DS_Store')
                except:
                    pass
                if tmp_list == []:
                    print('+++++++++++++++++++++++++++++++++++++++++++++++++++')
                print("[{}]--> [{}] is folder.".format(self.client_address[0],f_name))
                for i in tmp_list:
                    element_in_folder = os.path.join(f_name,i)
                    print("[{}]--> [{}] join into".format(self.client_address[0],element_in_folder))
                    element_in_folder = os.path.relpath(element_in_folder,self.USER_HOME_PATH)
                    print(self.USER_HOME_PATH)
                    print("##################################################")
                    print(element_in_folder)
                    self._fill_header(action='folder',filename=element_in_folder)
                    self._get(self.header)
                #   self.send_response(502)
            else:
                self.send_response(404)
        else:
            self.send_response(501)
            
###################################################################
#           此处服务器向客户端传参
# 函数直接copy的客户端的fill header   使用action来告诉客户端目标类型
###################################################################
#   从client里面抄的功能差不多有很多没用的功能，就算是冗余了    
    def _fill_header(self,action=None,filename=None,md5_opt=False,abs_path=None,relative_path=[]):
        self.header['action'] = action
        self.header['f_name'] = filename
        self.header['f_md5'] = md5_opt
        if action == 'file':
            self.header['f_size'] = os.stat(abs_path).st_size
        else:
            self.header['f_size'] = None
        self.header['rel_path'] = relative_path
        self.header['abs_path'] = abs_path
        print(self.header)
                
        
    def get_file_tree(self,path):
        pass
    def ls(self,*args,**kwargs):
        eval(os.system(args[0]))
    
if __name__ == '__main__':
    print("going to start server".center(60,'#'))
    server = socketserver.ThreadingTCPServer((settings.HOST,settings.PORT),FTPHandler)
    server.serve_forever()