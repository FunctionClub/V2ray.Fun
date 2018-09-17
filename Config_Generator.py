#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
import urllib2
import commands

def getip():
    myip = urllib2.urlopen('https://jp.fdos.me/ip/').read()
    myip = myip.strip()
    return str(myip)

def open_port(port):
    cmd =[ "iptables -I INPUT -m state --state NEW -m tcp -p tcp --dport $1 -j ACCEPT",
            "iptables -I INPUT -m state --state NEW -m udp -p udp --dport $1 -j ACCEPT",
            "ip6tables -I INPUT -m state --state NEW -m tcp -p tcp --dport $1 -j ACCEPT",
            "ip6tables -I INPUT -m state --state NEW -m udp -p udp --dport $1 -j ACCEPT"]

    for x in cmd:
        x = x.replace("$1",str(port))
        commands.getoutput(x)

def gen_server():

    data_file = open("/usr/local/V2ray.Fun/v2ray.config", "r")
    data = json.loads(data_file.read())
    data_file.close()

    server_websocket = json.loads("""
    {
  "path": "",
  "headers": {
    "Host": ""
  }
}
    """)

    server_mkcp = json.loads("""
    {
        "uplinkCapacity": 20,
        "downlinkCapacity": 100,
        "readBufferSize": 2,
        "mtu": 1350,
        "header": {
          "request": null,
          "type": "none",
          "response": null
        },
        "tti": 50,
        "congestion": false,
        "writeBufferSize": 2
      }
    """)

    server_tls = json.loads("""
    {
                "certificates": [
                    {
                        "certificateFile": "/path/to/example.domain/fullchain.cer",
                        "keyFile": "/path/to/example.domain.key"
                    }
                ]
            }
    """)

    server_raw = """
{
    "log": {
        "access": "/var/log/v2ray/access.log",
        "error": "/var/log/v2ray/error.log",
        "loglevel": "info"
    },
    "inbound": {
        "port": 39885,
        "protocol": "vmess",
        "settings": {
            "clients": [
                {
                    "id": "475161c6-837c-4318-a6bd-e7d414697de5",
                    "level": 1,
                    "alterId": 100
                }
            ]
        },
        "streamSettings": {
            "network": "ws"
        }
    },
    "outbound": {
        "protocol": "freedom",
        "settings": {}
    },
    "outboundDetour": [
        {
            "protocol": "blackhole",
            "settings": {},
            "tag": "blocked"
        }
    ],
    "routing": {
        "strategy": "rules",
        "settings": {
            "rules": [
                {
                    "type": "field",
                    "ip": [
                        "0.0.0.0/8",
                        "10.0.0.0/8",
                        "100.64.0.0/10",
                        "127.0.0.0/8",
                        "169.254.0.0/16",
                        "172.16.0.0/12",
                        "192.0.0.0/24",
                        "192.0.2.0/24",
                        "192.168.0.0/16",
                        "198.18.0.0/15",
                        "198.51.100.0/24",
                        "203.0.113.0/24",
                        "::1/128",
                        "fc00::/7",
                        "fe80::/10"
                    ],
                    "outboundTag": "blocked"
                }
            ]
        }
    }
}
    """
    server = json.loads(server_raw)
    if data['protocol'] == "vmess":
        server['inbound']['port'] = int(data['port'])
        server['inbound']['settings']['clients'][0]['id'] = data['uuid']
        server['inbound']['settings']['clients'][0]['security'] = data['encrypt']

    elif data['protocol'] == "mtproto":
        """ MTProto don't needs client config, just use Telegram"""
        server['inbound']['port'] = int(data['port'])
        server['inbound']['protocol'] = "mtproto"   
        server['inbound']['settings'] = dict()
        server['inbound']['settings']['users'] = list()
        server['inbound']['settings']['users'].append({'secret': data['secret']})
        server['inbound']['tag'] = "tg-in"

        server['outbound']['protocol'] = "mtproto"
        server['outbound']['tag'] = "tg-out"


        server['routing']['settings']['rules'].append({
            "type": "field",
            "inboundTag": ["tg-in"],
            "outboundTag": "tg-out"})

    if data['trans'] == "tcp":
        server['inbound']['streamSettings']=dict()
        server['inbound']['streamSettings']['network'] = "tcp"

    elif data['trans'].startswith("mkcp"):
        server['inbound']['streamSettings'] = dict()
        server['inbound']['streamSettings']['network'] = "kcp"
        server['inbound']['streamSettings']['kcpSettings'] = server_mkcp

        if data['trans'] == "mkcp-srtp":
            server['inbound']['streamSettings']['kcpSettings']['header']['type'] = "srtp"
        elif data['trans'] == "mkcp-utp":
            server['inbound']['streamSettings']['kcpSettings']['header']['type'] = "utp"
        elif data['trans'] == "mkcp-wechat":
            server['inbound']['streamSettings']['kcpSettings']['header']['type'] = "wechat-video"

    elif data['trans'] == "websocket":
        server['inbound']['streamSettings'] = dict()
        server['inbound']['streamSettings']['network'] = "ws"
        server['inbound']['streamSettings']['wsSettings'] = server_websocket
        server['inbound']['streamSettings']['wsSettings']['headers']['Host'] = data['domain']

    if data['tls'] == "on":
        server['inbound']['streamSettings']['security'] = "tls"
        server_tls['certificates'][0]['certificateFile'] = "/root/.acme.sh/{0}/fullchain.cer".format(data['domain'])
        server_tls['certificates'][0]['keyFile'] = "/root/.acme.sh/{0}/{0}.key".format(data['domain'],data['domain'])
        server['inbound']['streamSettings']['tlsSettings'] = server_tls

    server_file = open("/etc/v2ray/config.json","w")
    server_file.write(json.dumps(server,indent=2))
    server_file.close()


def gen_client():
    client_raw = """
    {
    "log": {
        "error": "error.log",
        "loglevel": "info"
    },
    "inbound": {
        "port": 1080,
        "listen": "127.0.0.1",
        "protocol": "socks",
        "settings": {
            "auth": "noauth",
            "ip": "127.0.0.1"
        }
    },
    "outbound": {
        "protocol": "vmess",
        "settings": {
            "vnext": [
                {
                    "address": "",
                    "port": 39885,
                    "users": [
                        {
                            "id": "475161c6-837c-4318-a6bd-e7d414697de5",
                            "alterId": 100,
                            "security": "auto"
                        }
                    ]
                }
            ]
        },
        "streamSettings": {
            "network": "ws"
        },
        "mux": {
            "enabled": false
        }
    },
    "inboundDetour": null,
    "outboundDetour": [
        {
            "protocol": "freedom",
            "settings": {},
            "tag": "direct"
        }
    ],
    "dns": {
        "servers": [
            "8.8.8.8",
            "8.8.4.4",
            "localhost"
        ]
    },
    "routing": {
        "strategy": "rules",
        "settings": {
            "domainStrategy": "IPIfNonMatch",
            "rules": [
                {
                    "type": "field",
                    "ip": [
                        "0.0.0.0/8",
                        "10.0.0.0/8",
                        "100.64.0.0/10",
                        "127.0.0.0/8",
                        "169.254.0.0/16",
                        "172.16.0.0/12",
                        "192.0.0.0/24",
                        "192.0.2.0/24",
                        "192.168.0.0/16",
                        "198.18.0.0/15",
                        "198.51.100.0/24",
                        "203.0.113.0/24",
                        "::1/128",
                        "fc00::/7",
                        "fe80::/10",
                        "geoip:cn"
                    ],
                    "domain": [
                        "geosite:cn"
                    ],
                    "outboundTag": "direct"
                },
                {
                    "type": "chinasites",
                    "outboundTag": "direct"
                },
                {
                    "type": "chinaip",
                    "outboundTag": "direct"
                }
            ]
        }
    }
}
    """

    cLient_mkcp = json.loads("""
    {
                "mtu": 1350,
                "tti": 50,
                "uplinkCapacity": 20,
                "downlinkCapacity": 100,
                "congestion": false,
                "readBufferSize": 2,
                "writeBufferSize": 2,
                "header": {
                    "type": "none"
                }
    }
    """)

    mux_enable = json.loads("""
    {
            "enabled": true
    }
    """)

    mux_disable = json.loads("""
    {
            "enabled": false
    }
    """)

    client = json.loads(client_raw)
    data_file = open("/usr/local/V2ray.Fun/v2ray.config", "r")
    data = json.loads(data_file.read())
    data_file.close()

    if data['mux'] == "on":
        client['outbound']['mux']['enabled'] = True
    elif data['mux'] == "off":
        client['outbound']['mux']['enabled'] = False

    if data['domain'] == "none":
        client['outbound']['settings']['vnext'][0]['address'] = data['ip']
    else:
        client['outbound']['settings']['vnext'][0]['address'] = data['domain']

    client['outbound']['settings']['vnext'][0]['port'] = int(data['port'])
    client['outbound']['settings']['vnext'][0]['users'][0]['id'] = data['uuid']
    client['outbound']['settings']['vnext'][0]['users'][0]['security'] = data['encrypt']


    if data['trans'] == "websocket":
        client['outbound']['streamSettings']['network'] = "ws"

    elif data['trans'].startswith("mkcp"):
        if data['trans'] == "mkcp-srtp":
            cLient_mkcp['header']['type'] = "srtp"
        elif data['trans'] == "mkcp-utp":
            cLient_mkcp['header']['type'] = "utp"
        elif data['trans'] == "mkcp-wechat":
            cLient_mkcp['header']['type'] = "wechat-video"

        client['outbound']['streamSettings']['network'] = "kcp"
        client['outbound']['streamSettings']['kcpSettings'] = cLient_mkcp

    elif data['trans'] == "tcp":
        client['outbound']['streamSettings']['network'] = "tcp"


    if data['tls'] == "on":
        client['outbound']['streamSettings']['security'] = "tls"

    client_file = open("/root/config.json","w")
    client_file.write(json.dumps(client,indent=2))
    client_file.close()

    client_file = open("/usr/local/V2ray.Fun/static/config.json", "w")
    client_file.write(json.dumps(client, indent=2))
    client_file.close()




