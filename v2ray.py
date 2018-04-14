#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import commands

def start():
    os.system("screen -dm python /usr/local/V2ray.Fun/app.py")

def stop():
    pids = commands.getoutput("""ps -ef | grep "app.py" | grep -v grep | awk '{print $2}'""")
    pids.split()
    for pid in pids:
        os.system("kill " + pid)

def write(data):
    data_file = open("/usr/local/V2ray.Fun/panel.config", "w")
    data_file.write(json.dumps(data,indent=2))
    data_file.close()

if __name__ == '__main__':
    data_file = open("/usr/local/V2ray.Fun/panel.config","r")
    data = json.loads(data_file.read())
    data_file.close()
    print("欢迎使用 V2ray.Fun 面板 ---- By 雨落无声\n")
    print("当前面板用户名：" + str(data['username']))
    print("当前面板密码：" + str(data['password']))
    print("当前面板监听端口：" + str(data['port']))
    print("请输入数字选择功能：\n")
    print("1. 启动面板")
    print("2. 停止面板")
    print("3. 重启面板")
    print("4. 设置面板用户名和密码")
    print("5. 设置面板SSL")
    print("6. 设置面板端口")
    choice = str(input("\n请选择："))

    if choice == "1":
        start()
        print("启动成功!")
        print(commands.getoutput("""ps -ef | grep "app.py" | grep -v grep"""))

    elif choice == "2":
        stop()
        print("停止成功！")

    elif choice == "3":
        stop()
        start()
        print("重启成功!")
    elif choice == "4":
        new_username = input("请输入新的用户名：")
        new_password = input("请输入心得密码：")
        data['username'] = new_username
        data['password'] = new_password
        write(data)
        stop()
        start()
        print("用户名密码设置成功！")
    elif choice == "5":
        print("提示：只有在面板开启 V2ray TLS 功能时，面板自身的SSL功能才会正常运行。\n")
        print("1. 打开面板 SSL 功能")
        print("2. 关闭面板 SSL 功能")
        ssl_choice = input("请选择：")

        if ssl_choice == "1":
            data['use_ssl'] = "on"
            write(data)
            stop()
            start()
            print("面板SSL已开启！")
        else:
            data['use_ssl'] = "off"
            write(data)
            stop()
            start()
            print("面板SSL已关闭！")
    elif choice == "6":
        new_port = input("请输入新的面板端口：")
        data['port'] = int(new_port)
        write(data)
        stop()
        start()
        print("面板端口已修改！")