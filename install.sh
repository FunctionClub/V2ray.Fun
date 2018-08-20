#!/usr/bin/env bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

#Check Root
[ $(id -u) != "0" ] && { echo "${CFAILURE}Error: You must be root to run this script${CEND}"; exit 1; }

#Check OS
if [ -n "$(grep 'Aliyun Linux release' /etc/issue)" -o -e /etc/redhat-release ]; then
  OS=CentOS
  [ -n "$(grep ' 7\.' /etc/redhat-release)" ] && CentOS_RHEL_version=7
  [ -n "$(grep ' 6\.' /etc/redhat-release)" -o -n "$(grep 'Aliyun Linux release6 15' /etc/issue)" ] && CentOS_RHEL_version=6
  [ -n "$(grep ' 5\.' /etc/redhat-release)" -o -n "$(grep 'Aliyun Linux release5' /etc/issue)" ] && CentOS_RHEL_version=5
elif [ -n "$(grep 'Amazon Linux AMI release' /etc/issue)" -o -e /etc/system-release ]; then
  OS=CentOS
  CentOS_RHEL_version=6
elif [ -n "$(grep bian /etc/issue)" -o "$(lsb_release -is 2>/dev/null)" == 'Debian' ]; then
  OS=Debian
  [ ! -e "$(which lsb_release)" ] && { apt-get -y update; apt-get -y install lsb-release; clear; }
  Debian_version=$(lsb_release -sr | awk -F. '{print $1}')
elif [ -n "$(grep Deepin /etc/issue)" -o "$(lsb_release -is 2>/dev/null)" == 'Deepin' ]; then
  OS=Debian
  [ ! -e "$(which lsb_release)" ] && { apt-get -y update; apt-get -y install lsb-release; clear; }
  Debian_version=$(lsb_release -sr | awk -F. '{print $1}')
elif [ -n "$(grep Ubuntu /etc/issue)" -o "$(lsb_release -is 2>/dev/null)" == 'Ubuntu' -o -n "$(grep 'Linux Mint' /etc/issue)" ]; then
  OS=Ubuntu
  [ ! -e "$(which lsb_release)" ] && { apt-get -y update; apt-get -y install lsb-release; clear; }
  Ubuntu_version=$(lsb_release -sr | awk -F. '{print $1}')
  [ -n "$(grep 'Linux Mint 18' /etc/issue)" ] && Ubuntu_version=16
else
  echo "${CFAILURE}Does not support this OS, Please contact the author! ${CEND}"
  kill -9 $$
fi

#Install Needed Packages

if [ ${OS} == Ubuntu ] || [ ${OS} == Debian ];then
	apt-get update -y
	apt-get install wget curl socat git unzip python python-dev openssl libssl-dev ca-certificates supervisor -y
	wget -O - "https://bootstrap.pypa.io/get-pip.py" | python
	pip install --upgrade pip
	pip install flask requests urllib3 Flask-BasicAuth Jinja2 requests six wheel
	pip install pyOpenSSL
fi

if [ ${OS} == CentOS ];then
	yum install epel-release -y
	yum install python-pip python-devel socat ca-certificates openssl unzip git curl crontabs wget -y
	pip install --upgrade pip
	pip install flask requests urllib3 Flask-BasicAuth supervisor Jinja2 requests six wheel
	pip install pyOpenSSL
fi

if [ ${Debian_version} == 9 ];then
	wget -N --no-check-certificate https://raw.githubusercontent.com/FunctionClub/V2ray.Fun/master/enable-debian9-rclocal.sh
	bash enable-debian9-rclocal.sh
	rm enable-debian9-rclocal.sh
fi

#Install acme.sh
curl https://get.acme.sh | sh

#Install V2ray
curl -L -s https://install.direct/go.sh | bash

#Install V2ray.Fun
cd /usr/local/
git clone https://github.com/FunctionClub/V2ray.Fun

#Generate Default Configurations
cd /usr/local/V2ray.Fun/ && python init.py
cp /usr/local/V2ray.Fun/v2ray.py /usr/local/bin/v2ray
chmod +x /usr/local/bin/v2ray
chmod +x /usr/local/V2ray.Fun/start.sh

#Start All services
service v2ray start

#Configure Supervisor
mkdir /etc/supervisor
mkdir /etc/supervisor/conf.d
echo_supervisord_conf > /etc/supervisor/supervisord.conf
cat>>/etc/supervisor/supervisord.conf<<EOF
[include]
files = /etc/supervisor/conf.d/*.ini
EOF
touch /etc/supervisor/conf.d/v2ray.fun.ini
cat>>/etc/supervisor/conf.d/v2ray.fun.ini<<EOF
[program:v2ray.fun]
command=/usr/local/V2ray.Fun/start.sh run
stdout_logfile=/var/log/v2ray.fun
autostart=true
autorestart=true
startsecs=5
priority=1
stopasgroup=true
killasgroup=true
EOF


read -p "请输入默认用户名[默认admin]： " un
read -p "请输入默认登录密码[默认admin]： " pw
read -p "请输入监听端口号[默认5000]： " uport
if [[ -z "${uport}" ]];then
	uport="5000"
else
	if [[ "$uport" =~ ^(-?|\+?)[0-9]+(\.?[0-9]+)?$ ]];then
		if [[ $uport -ge "65535" || $uport -le 1 ]];then
			echo "端口范围取值[1,65535]，应用默认端口号5000"
			unset uport
			uport="5000"
		else
			tport=`netstat -anlt | awk '{print $4}' | sed -e '1,2d' | awk -F : '{print $NF}' | sort -n | uniq | grep "$uport"`
			if [[ ! -z ${tport} ]];then
				echo "端口号已存在！应用默认端口号5000"
				unset uport
				uport="5000"
			fi
		fi
	else
		echo "请输入数字！应用默认端口号5000"
		uport="5000"
	fi
fi
if [[ -z "${un}" ]];then
	un="admin"
fi
if [[ -z "${pw}" ]];then
	pw="admin"
fi
sed -i "s/%%username%%/${un}/g" /usr/local/V2ray.Fun/panel.config
sed -i "s/%%passwd%%/${pw}/g" /usr/local/V2ray.Fun/panel.config
sed -i "s/%%port%%/${uport}/g" /usr/local/V2ray.Fun/panel.config
chmod 777 /etc/v2ray/config.json
supervisord -c /etc/supervisor/supervisord.conf
echo "supervisord -c /etc/supervisor/supervisord.conf">>/etc/rc.local
chmod +x /etc/rc.local

echo "安装成功！
"
echo "面板端口：${uport}"
echo "默认用户名：${un}"
echo "默认密码：${pw}"
echo ''
echo "输入 v2ray 并回车可以手动管理网页面板相关功能"

#清理垃圾文件
rm -rf /root/config.json
rm -rf /root/install-debian.sh
