#_*_coding:utf-8_*_
import optparse
import socketserver
from conf import settings
from core.ftp_server import FTPHandler

class ArvgHandler():
    def __init__(self):
        self.parser = optparse.OptionParser()
        #   self.parser.add_option("-h","--host",dest="host",help="Server binding host address.")
        #   self.parser.add_option("-p","--port",dest="port",help="Server binding port.")
        (self.option,self.args) = self.parser.parse_args()
        self.verify_args(self.option,self.args)
        
    #   效验功能
    def verify_args(self,option,args):       
         if len(args) != 0:
            if hasattr(self,args[0]):
                func = getattr(self,args[0])
                func()
            else:
                self.parser.print_help()
            
    def start(self):
        print("going to start server".center(30,'#'))
        server = socketserver.ThreadingTCPServer((settings.HOST,settings.PORT),FTPHandler)
        server.serve_forever()