# tiny_FTP
+ 最近准备一个复试，祝我好运朋友们。项目基本能用
  + ls
  + push
  + fetch
  + logout quit q
都是基本功能。可以用
#### FtpServer
    +     1、用户加密认证
    +     2、允许同时多用户登录
    +     3、每个用户有自己的家目录 ，且只能访问自己的家目录
    +     4、对用户进行磁盘配额，每个用户的可用空间不同
    +     5、允许用户在ftp server上随意切换目录
    +     6、允许用户查看当前目录下文件
    +     7、允许上传和下载文件，保证文件一致性
    +     8、文件传输过程中显示进度条
    +     9、附加功能：支持文件的断点续传
#####   回顾一些小知识点
+   dict.update({...}):向字典中更新元素，如果元素是之前没有的那么添加，如果元素存在且value不变，那么更新value值。
+   将传入的字符串转化为call，使用eval方法
+   python中for循环可以使用else来进入下一个判断循环
```
for i in range(1,3)
    print(i)
else:
    print("hello")
    
>>> 1
>>> 2
>>> hello
```
```
状态码
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
报头
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
字符串格式：
print("[{}]: ".format(self._username.strip()))
```
