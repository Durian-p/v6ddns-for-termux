import json
import time
import requests
import subprocess

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

from requests import RequestException


def main():
    config = {}
    accountInfo = {}
    dnsInfos = []
    try:
        config = readJson('/data/data/com.termux/files/home/repo/v6ddns/config.json')
        # 获取账户信息
        accountInfo = config['accountInfo']
        # 获取需要更新的dns信息
        dnsInfos = config['dnsInfos']
    except KeyError:
        print('未配置基础信息')
    except BaseException:
        print('未正常读取配置文件')

    # 获取ipv6地址
    ipv6 = getIpv6()
    # 请求api实现ddns
    for i in dnsInfos:
        i['content'] = ipv6
        dnsApi(accountInfo, dnsInfo=i)

    # 再给自己的服务器发一份，CloudFlare可能更新慢，可以从自己服务器上获取ip，直接ip访问
    myServer = config.get('myServer', None)
    if myServer is None:
        print('未配置个人服务器，跳过个人服务更新')
        exit(0)
    # 用了私钥签名验证身份
    data = None
    try:
        private_key_path = config['privateKPath']
        data = signature(private_key_path, b'QNha2Ry1XfLHcpXGG65I')
    except KeyError:
        print('未配置私钥，尝试不进行签名')
    myserverMsg = updateMy(myServer, ipv6, data)

    if len(myserverMsg) < 100:
        print(getTimeStr() + myserverMsg)


def getIpv6():
    cmd = "ip -6 addr list scope global | grep 'inet6' | sed -n 's/.*inet6 \\([0-9a-f:]\\+\\).*/\\1/p' | head -n 1"
    # 获取ipv6
    for i in range(5):
        try:
            output = exCmd(cmd).replace('\t', '').replace('\n', '').replace(' ', '')
            print('output:('+output + ')')
            if output == '' or len(output) < 6:
                raise BaseException
            print(getTimeStr() + '本机当前ipv6为: ' + output)
            return output
        except BaseException:
            print(getTimeStr() + "无法获取ipv6地址，尝试重启wifi")
            restartWifi()
            time.sleep(6)
        if i == 4:
            print('获取ip失败')
            exit(1)


def restartWifi():
    output = exCmd('adb devices | grep 127.0.0.1')
    if output.find('device') != -1:
        print(getTimeStr() + 'adb已连接,开始尝试重启wifi')
    else:
        print(getTimeStr() + 'adb未连接,wifi重启失败,需要等待手动重启wifi或等待手机重新获取ipv6')
        exit(1)
    basecmd = 'adb shell svc wifi '
    # 这个命令会打开手机屏幕
    exCmd('adb shell input keyevent 27')
    exCmd(basecmd + 'disable')
    time.sleep(1)
    exCmd(basecmd + 'enable')
    # 这个命令返回true是显示了锁屏界面，证明手机未解锁使用，直接关掉屏幕
    if exCmd('adb shell dumpsys window policy | awk "/KeyguardServiceDelegate/,/showingAndNotOccluded=true/" | grep '
             '-o "showing=[^ ]*" | cut -d "=" -f 2').find('true') != -1:
        for i in range(1, 10):
            time.sleep(7)
            if not checkWifi():
                exCmd('adb shell input tap 300 300')
            if i == 10:
                print('wifi重启失败，需要等待手动重启wifi或等待手机重新获取ipv6')
                exit(1)
        # 这个命令相当于按下锁屏键，可以亮屏也可以熄屏
        exCmd('adb shell input keyevent 26')


def checkWifi():
    cmd = 'adb shell dumpsys connectivity | grep NetworkAgentInfo'
    if exCmd(cmd == ''):
        return False
    return True



def dnsApi(accountInfo, dnsInfo):
    apiUrl = 'https://api.cloudflare.com/client/v4/zones/%s/dns_records/%s' % (
        accountInfo['zones'], dnsInfo['dns_records']
    )

    dnsInfo.pop('dns_records')
    body = dnsInfo

    headers = {
        'user-agent': 'Mozilla/5.0',
        'X-Auth-Email': accountInfo['email'],
        'X-Auth-Key': accountInfo['api'],
        'Content-Type': 'application/json'
    }

    request = requests.put(apiUrl, headers=headers, json=body)
    res = json.loads(request.text)
    if request.status_code == 200:
        return print(getTimeStr() + dnsInfo['name'] + ": Success!")
    else:
        print(getTimeStr() + str(res['messages']))
        print(getTimeStr() + str(res['errors']))
        return print(getTimeStr() + dnsInfo['name'] + ": Fail!")



def updateMy(myServer, ipv6, data):
    myserverMsg = ''
    for i in range(1, 3):
        try:
            request = requests.post('http://' + myServer + '/papi/newv6?ipv6=' + ipv6, data=data, timeout=5)
            if request.status_code == 403:
                myserverMsg = 'Update Failed. Permission Denied.'
                break
            elif request.status_code != 200:
                raise RequestException()
            else:
                if request.text == 'OK':
                    myserverMsg = 'Update My Server Success!'
                    break
                else:
                    raise BaseException
        except BaseException:
            myserverMsg = 'Update Shanghai Server Failed. Shanghai Server Error.'
            if i > 1:
                time.sleep(1)
    return myserverMsg


def exCmd(command):
    return subprocess.check_output(command, shell=True, text=True)


# 获取格式化时间字符串
def getTimeStr():
    return '[ ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ' ]  '


def readJson(path):
    with open(path, 'r+') as f:
        temp = f.read()
        if temp == '':
            f.write("{}")
            return {}
        f_data = json.loads(temp)
        return f_data


def signature(private_key_path, message, password=None):
    with open(private_key_path, 'rb') as pkf:
        private_key = serialization.load_pem_private_key(
            pkf.read(),
            password=password,
            backend=default_backend()
        )
        # 使用私钥进行签名
        return private_key.sign(
            message,
            padding.PKCS1v15(),
            hashes.SHA256()
        )


if __name__ == '__main__':
    main()
