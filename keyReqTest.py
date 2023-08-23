import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding


def main():
    ipv6 = '240e:380:753e:610:8a92:6f66:428f:b550'
    private_key_path = 'client/private_key.pem'
    header = {
        'user-agent': 'Mozilla/5.0',
        'Content-Type': 'application/json'
    }

    data = signature(private_key_path, b'QNha2Ry1XfLHcpXGG65I')
    request = requests.post('http://[fe80::acbc:4605:6ca1:c8a6]:6677/papi/newv6?ipv6='+ipv6, headers=header, data=data)
    print(request.text)


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


main()
