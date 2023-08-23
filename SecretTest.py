from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding


# 加载私钥
def load_private_key(file_path, password=None):
    with open(file_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=password,
            backend=default_backend()
        )
    return private_key


# 要签名的字符串
message = b"Hello, this is the message to be signed."

# 从文件加载私钥
private_key_file = "client/private_key.pem"
private_key = load_private_key(private_key_file, password=None)

# 使用私钥进行签名
signature = private_key.sign(
    message,
    padding.PKCS1v15(),
    hashes.SHA256()
)

# 打印签名
print("签名：")
print(signature)


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


# 加载公钥
public_key_file = "myserver/public_key.pem"
public_key = load_public_key(public_key_file)

# 要验证的签名
# 假设之前使用私钥对 message 进行了签名并得到了 signature
# signature = ...

# 验证签名是否正确
is_valid = verify_signature(public_key, message, signature)

if is_valid:
    print("签名验证通过")
else:
    print("签名验证失败")
