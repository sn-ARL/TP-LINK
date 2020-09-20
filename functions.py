import requests
from des import DesKey as DKey
import netifaces
import subprocess
import js
import re
import os


def login(login, password):
    #token = 'Authorization=Basic%20YWRtaW46MjEyMzJmMjk3YTU3YTVhNzQzODk0YTBlNGE4MDFmYzM%3D'
    t = 'Authorization=' + js.escape(login, password)
    gateways = netifaces.gateways()
    router_ip = 'http://'+gateways['default'][netifaces.AF_INET][0]
    r = requests.get(router_ip+'/userRpm/LoginRpm.htm?Save=Save',headers={'Referer':router_ip+'/','Cookie': t})
    if not 140 < len(r.content) < 160:
        return None, None, None
    str_r = str(r.content)
    session = str_r[-64:-48]
    return router_ip, t, session

def logout(router_ip, session, t):
    requests.get(router_ip+'/'+session+'/userRpm/LogoutRpm.htm',headers={'Referer':router_ip+'/'+session+'/userRpm/MenuRpm.htm','Cookie': t})
    return None

def get_config(router_ip, t, session):
    r = requests.get(router_ip+'/'+session+'/userRpm/config.bin',headers={'Referer':router_ip+'/','Cookie': t})
    text = r.content
    key = DKey(b'\x47\x8D\xA5\x0B\xF9\xE3\xD2\xCF')
    config = str(key.decrypt(text))[:-2]
    
    config = config[config.find('product_id'):config.find('\\r\\n\\x00')]

    temp_pars = config.split('\\r\\')
    settings = dict()                                       #словарь с настройками роутера

    for elem in temp_pars:
        try:
            settings[elem.split()[0]] = elem.split(' ',1)[1]
        except:
            pass

    file = open('file1.txt', 'w')
    for e in settings:
        file.write(e + ' '+ settings[e]+ '\n')
    file.close()

    bssid = True if settings['nwlan_ssid_brd'] == '0' else False
    guest = True if settings['nwireless_guestNetwork_status'] == '1' else False
    wps = True if settings['nwlan_wps_en'] == '0' else False
    pwr = True if settings['nwlan_pwr'] != '0' else False
    remote = True if settings['nrmt_en'] == '0' else False
    upnp = True if settings['nupnp_en'] == '0' else False
    mac = True if settings['nloc_manage_en'] == '1' else False

    return (bssid, guest, wps, pwr, remote, upnp, mac)

def get_wifi_sec(router_ip, t, session):
    r = requests.get(router_ip+'/'+session+'/userRpm/WlanSecurityRpm.htm',headers={'Referer':router_ip+'/','Cookie': t})
    text = str(r.content)
    place = text.find(',')
    protec = False
    enc = False
    b = text.find('(')+1
    e = text.find(');')
    text = text[b:e].split(',')
    if text[1] == ' 1' and text[3][-2] == '2':
        protec = True
    if text[14] == ' 3':
        enc = True
    return protec, enc

def get_wifi_pass(ssid):
    if os.name == 'nt':
        #windows
        cmd = subprocess.check_output('netsh wlan show profile ' + ssid + ' key = clear').decode('cp866')
        place = cmd.find('Содержимое ключа')
        return cmd[place+30:cmd.find('\r', place)]
    else:
        #linux
        cmd = subprocess.check_output('sudo grep psk= /etc/NetworkManager/system-connections/*')
        name = cmd.find(ssid)
        end = cmd.find('*\\n',name)
        return cmd[place+len(ssid)+6:end]

    
def get_mac_f(router_ip, t, session):
    r = requests.get(router_ip+'/'+session+'/userRpm/WlanMacFilterRpm.htm',headers={'Referer':router_ip+'/','Cookie': t})
    text = str(r.content)
    place = text.find(',')
    if text[place-1:place] == '0':
        return False            #OFF
    else:
        return True             #ON

def get_guest_access(router_ip, t, session):
    r = requests.get(router_ip+'/'+session+'/userRpm/GuestNetWirelessCfgRpm.htm',headers={'Referer':router_ip+'/','Cookie': t})
    text = str(r.content)
    b = text.find('(')
    e = text.find(');')
    text = text[b:e].split(',')[5][2]
    if text == '1':
        return True     #ON
    else:
        return False    #OFF
  
def get_mac():
    gateway = netifaces.gateways()
    interface = gateway['default'][netifaces.AF_INET][1]
    mac = netifaces.ifaddresses(interface)[netifaces.AF_LINK][0]['addr']
    return js.ctx.call("hex_md5", mac)

def wifi_sec_on(router_ip, t, session, pas='76953224'):
    try:
        requests.get(router_ip+'/'+session+'/userRpm/WlanSecurityRpm.htm?\
secType=3&pskSecOpt=2&pskCipher=3&pskSecret='+pas+'&interval=0&wpaSec\
Opt=3&wpaCipher=1&radiusIp=&radiusPort=1812&radiusSecret=&intervalWpa=0\
&wepSecOpt=3&keytype=1&keynum=1&key1=&length1=0&key2=&length2=0&key3=&le\
ngth3=0&key4=&length4=0&Save=%D0%A1%D0%BE%D1%85%D1%80%D0%B0%D0%BD%D0%B8%D1\
%82%D1%8C',headers={'Referer':router_ip+'/'+session+'/userRpm/WlanSecurityRpm.htm','Cookie': t})
    except OSError:
        return None

def get_ssid(router_ip, t, session):
    r = requests.get(router_ip+'/'+session+'/userRpm/WlanNetworkRpm.htm',headers={'Referer':router_ip+'/'+session+'/userRpm/WlanNetworkRpm.htm','Cookie': t})
    begin = r.content.find(b'"',70)+1
    end = r.content.find(b'"',begin)
    return str(r.content[begin:end])[2:-1]

def ssid(router_ip, t, session):
    ssid = get_ssid(router_ip, t, session)
    requests.get(router_ip+'/'+session+'/userRpm/WlanNetworkRpm.htm?ssid1\
='+ssid+'&region=83&band=0&mode=6&chanWidth=2&channel=15&rate=71&ap=1&brls\
sid=&brlbssid=&addrType=1&keytype=1&wepindex=1&authtype=1&keytext=&Save=%D0%A1%D\
0%BE%D1%85%D1%80%D0%B0%D0%BD%D0%B8%D1%82%D1%8C',headers={'Referer':router_ip+'/'+session+'/userRpm/WlanNetworkRpm.htm','Cookie': t})
    return None

#"0123456789ABCDEFabcdefGHIJKLMNOPQRSTUVWXYZghijklmnopqrstuvwxyz`~!@#$^&*()-=_+[]{};:\'\"\\|/?.,<>/% "
def pass_checker(pas):
    power = 183000              #скорость подбора
    threshold = 365*24*60*60    #пороговое значение
    symbols = 0
    if pas.upper() != pas:      #проверка на маленькие буквы
        symbols+=26
    if pas.lower() != pas:      #проверка на большие буквы
        symbols+=26
    if re.findall('\d', pas):   #проерка на числа
        symbols+=10
    if re.findall('\W', pas) or '_' in pas:
        symbols+=34
    return True if symbols**len(pas)/power > threshold else False

def login_checker(login):
    names = ['root', 'user', 'admin', 'administrator']
    if login.lower() in names:
        return False
    else:
        return True

def router_login_pass_changer(router_ip, t, session, old_username, old_password, new_username, new_password):
    requests.get(router_ip+'/'+session+'/userRpm/ChangeLoginPwdRpm.htm?\
oldname='+old_username+'&oldpassword='+js.pass_hash(old_password)+'&\
newname='+new_username+'&newpassword='+js.pass_hash(new_password)+'&newpassword2='+js.pass_hash(new_password)+'&Save=%D0%A1%D\
0%BE%D1%85%D1%80%D0%B0%D0%BD%D0%B8%D1%82%D1%8C',headers={'Referer':router_ip+'/'+session+'/userRpm/ChangeLoginPwdRpm.htm','Cookie': t})
    return None

def mac_filter_en(router_ip, t, session, mac):
    requests.get(router_ip+'/'+session+'/userRpm/LocalManageControlRpm.htm?\
enableWhitelist=1&mac0='+mac+'&Save=%D0%A1%D\
0%BE%D1%85%D1%80%D0%B0%D0%BD%D0%B8%D1%82%D1%8C',headers={'Referer':router_ip+'/'+session+'/userRpm/LocalManageControlRpm.htm','Cookie': t})
    return None

def antenna_changer(router_ip, t, session, mode):
    requests.get(router_ip+'/'+session+'/userRpm/WlanAdvRpm.htm?\
txPower='+mode+'&Save=%D0%A1%D\
0%BE%D1%85%D1%80%D0%B0%D0%BD%D0%B8%D1%82%D1%8C',headers={'Referer':router_ip+'/'+session+'/userRpm/WlanAdvRpm.htm','Cookie': t})
    return None  

def wps_off(router_ip, t, session):
    requests.get(router_ip+'/'+session+'/userRpm/WpsCfgRpm.htm?\
DisWps=%D0%9E%D1%82%D0%BA%D0%BB%D1%8E%D1%87%D0%B8%D1%82%D1%8C',headers={'Referer':router_ip+'/'+session+'/userRpm/WpsCfgRpm.htm','Cookie': t})
    return None 

def remote_off(router_ip, t, session):
    requests.get(router_ip+'/'+session+'/userRpm/ManageControlRpm.htm?\
port=80&ip=0.0.0.0&&Save=%D0%A1%D\
0%BE%D1%85%D1%80%D0%B0%D0%BD%D0%B8%D1%82%D1%8C',headers={'Referer':router_ip+'/'+session+'/userRpm/ManageControlRpm.htm','Cookie': t})
    return None

def upnp_off(router_ip, t, session):
    requests.get(router_ip+'/'+session+'/userRpm/UpnpCfgRpm.htm?\
upnpenb=Disable&Upnpdisable=%D0%9E%D1%82%D0%BA%D0%BB%D1%8E%D1%87%\
D0%B8%D1%82%D1%8C',headers={'Referer':router_ip+'/'+session+'/userRpm/UpnpCfgRpm.htm','Cookie': t})
    return None

def guest_on(router_ip, t, session, ssid = 'TP-LINK_GUEST_C5C0', password='76953224'):
    requests.get(router_ip+'/'+session+'/userRpm/GuestNetWirelessCfgRpm.htm?\
up_bandWidth=256&down_bandWidth=1024&guestNetMode=1&ssid='+ssid+'&SecOpt=3&\
pskSecOpt=2&pskCipher=3&pskSecret='+password+'&interval=0&AccessTime=1&timeouthour=0&timeoutmin=0\
&scheDay=0&daysAll=0&Save=%D0%A1%D0%BE%D1%85%D1%80%D0%B0%D0%BD%D0%B8%D1%82%D1%8C',headers={'Referer':router_ip+'/'+session+'/userRpm/GuestNetWirelessCfgRpm.htm','Cookie': t})
    return None

def soft(router_ip, t, session):
    r = str(requests.get('https://www.tp-link.com/ru/support/download/tl-wr740n/v6/#Firmware').content)
    e = r.find('.zip')
    site_version = r[e-6:e]
    r = str(requests.get(router_ip+'/'+session+'/userRpm/StatusRpm.htm',headers={'Referer':router_ip+'/','Cookie': t}).content)
    b = r.find('Build ')+6
    e = r.find(' Rel.')
    router_version = r[b:e]
    if router_version == site_version:
        return True
    else:
        return False
    #'https://www.tp-link.com/ru/support/download/tl-wr740n/v6/#Firmware'

def data_checker(data, mode):
    chars = "0123456789ABCDEFabcdefGHIJKLMNOPQRSTUVWXYZghijklmnopqrstuvwxyz`~!@#$^&*()-=_+[]{};:\'\"\\|/?.,<>/% "
    if mode == 0:           #пароль от wifi
        if not 7<len(data)<64:
            return False
    elif mode == 1:         #логин или пароль от роутера
        if len(data)>15:
            return False
        chars = chars[:-1]
    else:                   #mac
        pattern = r'((\w)(\w)-(\w)(\w)-(\w)(\w)-(\w)(\w)-(\w)(\w)-(\w)(\w))'
        if re.fullmatch(pattern, data) == None:
            return False
        chars = chars[:62]

    for char in data:
        if char not in chars:
            return False
    return True

    
