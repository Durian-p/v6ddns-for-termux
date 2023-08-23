from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from flask import Flask, request
import json

app = Flask(__name__)


@app.route('/papi/newv6', methods=('POST',))
def update():
    newIp = request.args.get('ipv6', None)
    signature = request.data
    if newIp is None:
        print('Empty ipv6.')
        return 'INVALID ATTRIBUTE', 400
    if not signature:
        print('Empty signature data.')
        return 'NO PERMISSION', 401
    message = b'QNha2Ry1XfLHcpXGG65I'
    # 加载公钥
    public_key_file = "public_key.pem"
    public_key = load_public_key(public_key_file)
    # 验证签名是否正确
    is_valid = verify_signature(public_key, message, signature)

    if is_valid:
        print("Signature is valid. Updating ipv6.")
        print(newIp)
        try:
            writeInfo(ipv6=newIp)
        except BaseException as ex:
            print('Update failed! ')
            print(ex)
            return 'FAILED TO UPDATE', 500
        return 'OK', 200
    else:
        print("Signature is not valid.")
        return 'NO PERMISSION', 403


# 返回信息页面html
@app.route('/papi/newv6', methods=('GET',))
def getv6():
    try:
        data = readInfo()
        ip = data.get('ipv6', None)
        return {'ipv6': ip}
    except BaseException:
        return {
            'ipv6': None,
            'error': 'There is an error occur when reading new IPv6 address. This might be caused by the '
                     'wrongly edited data file or the absence of it. Please check \'data.json.\''
            }


def readInfo():
    with open('data.json', 'r+') as f:
        temp = f.read()
        if temp == '':
            f.write("{}")
            return {}
        f_data = json.loads(temp)
        return f_data


def writeInfo(**kw):
    f_data = readInfo()
    f_data.update(kw)
    with open('data.json', 'w') as f:
        f.write(json.dumps(f_data, indent=4))


# 加载公钥
def load_public_key(file_path):
    with open(file_path, "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )
    return public_key


# 验证签名
def verify_signature(public_key, message, signature):
    try:
        public_key.verify(
            signature,
            message,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except:
        return False


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6677)
