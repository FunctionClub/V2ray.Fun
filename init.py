#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
import config_generator
import uuid

data = {}
with open("/usr/local/V2ray.Fun/v2ray.config") as f:
    data = json.load(f)

data['uuid'] = str(uuid.uuid4())
data['ip'] = config_generator.getip()
config_generator.open_port(data['port'])

with open("/usr/local/V2ray.Fun/v2ray.config", "w") as f:
    f.write(json.dump(data))

config_generator.gen_server()
config_generator.gen_client()
