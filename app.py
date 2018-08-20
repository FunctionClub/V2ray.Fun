#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask,render_template,request
import os
from Config_Generator import *
from flask_basicauth import BasicAuth

panel_config_file = open("panel.config","r")
panel_config = json.loads(panel_config_file.read())
panel_config_file.close()


app = Flask(__name__,static_url_path='/static')

app.config['BASIC_AUTH_USERNAME'] = panel_config['username']
app.config['BASIC_AUTH_PASSWORD'] = panel_config['password']
app.config['BASIC_AUTH_FORCE'] = True
basic_auth = BasicAuth(app)

def change_config(config,value):
    old_config = open("v2ray.config", "r")
    old_json = json.loads(old_config.read())
    old_config.close()
    old_json[str(config)] = str(value)

    config = open("v2ray.config","w")
    string = str(json.dumps(old_json,indent=2))
    config.write(string)
    config.close()




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

@app.route('/set_protocol', methods=['GET', 'POST'])
def set_protocol():
    items = request.args.to_dict()
    if items['protocol'] == "1" :
        change_config('protocol', 'vmess')
    elif items['protocol'] == "2":
        change_config('protocol', 'mtproto')
    gen_server()
    gen_client()
    return "OK"

@app.route('/set_secret', methods=['GET', 'POST'])
def set_secret():
    items = request.args.to_dict()
    change_config('secret', items['secret'])
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
    gen_client()
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

@app.route('/get_access_log')
def get_access_log():
    file = open('/var/log/v2ray/access.log',"r")
    content = file.read().split("\n")
    min_length = min(20,len(content))
    content = content[-min_length:]
    string = ""
    for i in range(min_length):
        string = string + content[i] + "<br>"
    return string

@app.route('/get_error_log')
def get_error_log():
    file = open('/var/log/v2ray/error.log',"r")
    content = file.read().split("\n")
    min_length = min(20,len(content))
    content = content[-min_length:]
    string = ""
    for i in range(min_length):
        string = string + content[i] + "<br>"
    return string



@app.route('/gen_ssl',methods=['GET', 'POST'])
def gen_ssl():
    items = request.args.to_dict()
    domain = str(items['domain'])

    stop_service()
    cmd = "bash /root/.acme.sh/acme.sh  --issue -d {0} --standalone".format(domain)
    check_acme = """ps -ef | grep "acme.sh" | grep -v grep | awk '{print $2}'"""
    commands.getoutput(cmd)
    acme_status = commands.getoutput(check_acme)
    while acme_status != "":
        acme_status = commands.getoutput(check_acme)

    result = os.path.exists("/root/.acme.sh/{0}/fullchain.cer".format(domain))
    start_service()
    if result == True:
        return "True"
    else:
        return "False"




data_file = open("v2ray.config", "r")
data = json.loads(data_file.read())
data_file.close()

if data['tls'] == "on" and panel_config['use_ssl'] == "on":
    key_file = "/root/.acme.sh/{0}/{0}.key".format(data['domain'],data['domain'])
    crt_file = "/root/.acme.sh/{0}/fullchain.cer".format(data['domain'])
    app.run(host='0.0.0.0', port=panel_config['port'],ssl_context=(crt_file, key_file))
else:
    app.run(host='0.0.0.0', port=panel_config['port'])



