#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
import Config_Generator
import uuid

data_file = open("/usr/local/V2ray.Fun/v2ray.config","r")
data = json.loads(data_file.read())
data_file.close()

data['uuid'] = str(uuid.uuid4())
data['ip'] = Config_Generator.getip()
Config_Generator.open_port(data['port'])


data_file = open("/usr/local/V2ray.Fun/v2ray.config","w")
data_file.write(json.dumps(data))
data_file.close()

Config_Generator.gen_server()
Config_Generator.gen_client()
