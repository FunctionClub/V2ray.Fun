#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask,render_template,request
import commands
import time
from Config_Generator import *



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


def open_port(port):
    cmd =[ "iptables -I INPUT -m state --state NEW -m tcp -p tcp --dport $1 -j ACCEPT",
            "iptables -I INPUT -m state --state NEW -m udp -p udp --dport $1 -j ACCEPT",
            "ip6tables -I INPUT -m state --state NEW -m tcp -p tcp --dport $1 -j ACCEPT",
            "ip6tables -I INPUT -m state --state NEW -m udp -p udp --dport $1 -j ACCEPT"]

    for x in cmd:
        x = x.replace("$1",str(port))
        commands.getoutput(x)



def get_status():
    cmd = """ps -ef | grep "v2ray" | grep -v grep | awk '{print $2}'"""
    output = commands.getoutput(cmd)
    if output=="":
        return "off"
    else:
        return "on"

@app.route('/start_service')
def start_service():
    cmd = "service v2ray start"
    commands.getoutput(cmd)
    change_config("status","on")
    return "OK"

@app.route('/stop_service')
def stop_service():
    cmd = "service v2ray stop"
    commands.getoutput(cmd)
    change_config("status", "off")
    return "OK"


@app.route('/restart_service')
def restart_service():
    cmd = "service v2ray restart"
    commands.getoutput(cmd)
    change_config("status", "on")
    return "OK"


@app.route('/set_uuid',methods=['GET', 'POST'])
def set_uuid():
    items = request.args.to_dict()
    change_config("uuid",items['setuuid'])
    gen_server()
    gen_client()
    restart_service()
    return "OK"

@app.route('/set_tls',methods=['GET', 'POST'])
def set_tls():
    items = request.args.to_dict()
    if(items['action'] == "off"):
        change_config('tls','off')
        change_config('domain','none')
    else:
        change_config("tls","on")
        change_config("domain",items['domain'])
    gen_server()
    gen_client()
    restart_service()

    return "OK"

@app.route('/set_mux',methods=['GET', 'POST'])
def set_mux():
    items = request.args.to_dict()
    change_config("mux",items['action'])
    return "OK"

@app.route('/set_port',methods=['GET', 'POST'])
def set_port():
    items = request.args.to_dict()
    change_config("port",items['setport'])
    gen_server()
    gen_client()
    restart_service()
    open_port(items['setport'])
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

    gen_server()
    gen_client()
    restart_service()

    return "OK"

@app.route('/set_trans',methods=['GET', 'POST'])
def set_trans():
    items = request.args.to_dict()
    trans = str(items['trans'])
    if trans == "1":
        change_config("trans","tcp")
        change_config("domain", "none")
    elif trans == "2":
        change_config("trans", "websocket")
        change_config("domain", items['domain'])
    elif trans == "3":
        change_config("trans", "mkcp")
        change_config("domain", "none")
    elif trans == "4":
        change_config("trans", "mkcp-srtp")
        change_config("domain", "none")
    elif trans == "5":
        change_config("trans", "mkcp-utp")
        change_config("domain", "none")
    else:
        change_config("trans","mkcp-wechat")
        change_config("domain", "none")

    gen_server()
    gen_client()
    restart_service()

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
    if(json_content['domain'] != "none"):
        json_content['ip'] = json_content['domain']

    json_content['status'] = get_status()
    json_dump = json.dumps(json_content)
    v2ray_config.close()
    return json_dump

@app.route('/get_log')
def get_log():
    file = open('/var/log/v2ray/access.log',"r")
    content = file.read().split("\n")
    min_length = min(15,len(content))
    content = content[-min_length:]
    string = ""
    for i in range(min_length):
        string = string + content[i] + "<br>"
    return string

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug = True)
