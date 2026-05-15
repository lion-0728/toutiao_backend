import json
from typing import Any

import redis.asyncio as redis

# 主机地址可能是localhost, 也可能是远程服务器的IP地址, 或者将来也可能是我们服务器的ip地址
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

# 创建 Redis 的连接对象
redis_client = redis.Redis(
    host=REDIS_HOST,  # redis 服务器主机地址
    port=REDIS_PORT,  # redis 端口号
    db=REDIS_DB,      # redis 数据库编号, 0-15
    decode_responses=True  # 是否将字节数据解码为字符串
)

# 设置 和 读取 (字符串 和 列表或字典) "[{}]"
# 读取: 字符串
async def get_cache(key: str):
    # return await redis_client.get(key)
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"获取缓存失败:{e}")
        return None

# 读取: 列表或字典
async def get_json_cache(key: str):
    try:
        # 从Redis(外部存储)获取数据 → 得到的是JSON格式的字符串
        data = await redis_client.get(key)
        if data:
            return json.loads(data)  # 反序列化:将JSON字符串 → 转换为Python内存中的字典/列表对象
        return None
    except Exception as e:
        print(f"获取 JSON 缓存失败:{e}")
        return None

# 设置缓存 setex(key, expire, value)
async def set_cache(key: str, value: Any, expire: int = 3600):
    try:
        if isinstance(value, (dict, list)):
            # 转字符串再存
            value = json.dumps(value, ensure_ascii=False)  # 中文正常保存
        await redis_client.setex(key, expire, value)
        return True
    except Exception as e:
        print(f"设置缓存失败:{e}")
        return False
