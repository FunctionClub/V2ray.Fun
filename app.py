#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask,render_template,request
import commands
import urllib2
import json
import time



app = Flask(__name__,static_url_path='/static')

def change_config(config,value):
    old_config = open("v2ray.config", "r")
    old_json = json.loads(old_config.read())
    old_config.close()
    old_json[str(config)] = str(value)

    config = open("v2ray.config","w")
    string = str(json.dumps(old_json))
    config.write(string)
    config.close()



def getip():
    myip = urllib2.urlopen('http://members.3322.org/dyndns/getip').read()
    myip = myip.strip()
    return str(myip)


@app.route('/set_uuid',methods=['GET', 'POST'])
def set_uuid():
    items = request.args.to_dict()
    change_config("uuid",items['setuuid'])
    return "OK"

@app.route('/set_port',methods=['GET', 'POST'])
def set_port():
    items = request.args.to_dict()
    change_config("port",items['setport'])
    return "OK"

@app.route('/set_encrypt',methods=['GET', 'POST'])
def set_encrypt():
    items = request.args.to_dict()
    encrypt = str(items['encrypt'])
    if encrypt == "1":
        change_config("encrypt","auto")
    elif encrypt == "2":
        change_config("encrypt", "aes-128-cfb")
    elif encrypt == "3":
        change_config("encrypt", "aes-128-gcm")
    elif encrypt == "4":
        change_config("encrypt", "chacha20-poly1305")
    else:
        change_config("encrypt", "none")

    return "OK"

@app.route('/set_trans',methods=['GET', 'POST'])
def set_trans():
    items = request.args.to_dict()
    trans = str(items['trans'])
    if trans == "1":
        change_config("trans","tcp")
    elif trans == "2":
        change_config("trans", "websocket")
    elif trans == "3":
        change_config("trans", "mkcp")
    elif trans == "4":
        change_config("trans", "mkcp-srtp")
    elif trans == "5":
        change_config("trans", "mkcp-utp")
    else:
        change_config("trans","mkcp-wechat")

    return "OK"


@app.route('/')
@app.route('/index.html')
def index_page():
    return render_template("index.html")

@app.route('/app.html')
def app_page():
    return render_template("app.html")

@app.route('/log.html')
def log_page():
    return render_template("log.html")

@app.route('/config.html')
def config_page():
    return render_template("config.html")

@app.route('/check_domain')
def check_domain():
    time.sleep(2)
    return "true"

@app.route('/get_info')
def get_info():
    v2ray_config = open("v2ray.config","r")
    json_content = json.loads(v2ray_config.read())
    json_dump = json.dumps(json_content)
    v2ray_config.close()
    return json_dump

@app.route('/get_log')
def get_log():
    file = open('t.txt',"r")
    content = file.read().split("\n")
    min_length = min(15,len(content))
    content = content[-min_length:]
    string = ""
    for i in range(min_length):
        string = string + content[i] + "<br>"
    return string

if __name__ == '__main__':
    app.run()
