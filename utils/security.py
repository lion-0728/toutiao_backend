# 方法一:passlibde的bug,不兼容bcrypt-5.0.0,可以降一下bcrypt版本:pip install bcrypt==4.1.3
# 方法二:改用 pbkdf2_sha256 算法,没有字节长度限制, passlib 原生支持,不会出现版本兼容问题,安全性相当(可以调整迭代次数)
# 运行的这边和讲解的这版有区别
import bcrypt as bcrypt_lib
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 密码加密
def get_hash_password(password: str):
    return pwd_context.hash(password)

# def get_hash_password(password: str):  # 定义密码加密方法
#     # bcrypt 限制密码最多72字节,自动截断
#     if len(password.encode('utf-8')) > 72:
#         password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
#
#     # 使用 bcrypt 库直接加密
#     salt = bcrypt_lib.gensalt()
#     hashed = bcrypt_lib.hashpw(password.encode('utf-8'), salt)
#     return hashed.decode('utf-8')

# # 验证密码
# def verify_password(plain_password: str, hashed_password: str):
#     if len(plain_password.encode('utf-8')) > 72:
#         plain_password = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
#     return bcrypt_lib.checkpw(
#         plain_password.encode('utf-8'),
#         hashed_password.encode('utf-8')
#     )

# 密码验证: verify 返回值是布尔型
def verify_password(plain_password,hashed_password):
    return pwd_context.verify(plain_password, hashed_password)