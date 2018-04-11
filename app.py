#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask,render_template
import commands
import urllib2
import json
import time;



app = Flask(__name__,static_url_path='/static')

def getip():
    myip = urllib2.urlopen('http://members.3322.org/dyndns/getip').read()
    myip = myip.strip()
    return str(myip)



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
    return """{
    "status": "off",
    "ip": "123.123.123.123",
    "uuid" : "dasdasd-das-d-asd-as-d-as",
    "port" : "4567",
    "encrypt" : "chacha20",
    "trans" : "mkcp 伪装微信流量",
    "tls" : "on",
    "mux" : "on"
    }
    """

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
