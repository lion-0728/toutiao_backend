from pydantic import BaseModel, field_validator, Field, ConfigDict
from typing import Any, Optional

class UserRequest(BaseModel):
    username: str
    password: str

    @field_validator('password', mode='before')
    @classmethod
    def validate_password_length(cls, v: Any) -> str:
        if isinstance(v, str) and len(v.encode('utf-8')) > 72:
            raise ValueError('密码长度不能超过72个字符')
        return v


# user_info 对应的类:基础类 + Info 类(id、用户名)
class UserInfoBase(BaseModel):
    """
    ⽤户信息基础数据模型
    """
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="个⼈简介")

class UserInfoResponse(UserInfoBase):
    id: int
    username: str

    # 模型类配置
    model_config = ConfigDict(
        from_attributes=True  # 允许从ORM对象属性中取值
    )

# data 数据类型
class UserAuthResponse(BaseModel):
    token: str
    user_info: UserInfoResponse = Field(..., alias='userInfo')

    # 模型类配置
    model_config = ConfigDict(
        populate_by_name=True,  # alias /字段名兼容
        from_attributes=True    # 允许从ORM对象属性中取值
    )

# 更新用户信息的模型类
class UserUpdateRequest(BaseModel):
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None

class UserChangePasswordRequest(BaseModel):
    old_password: str = Field(..., alias="oldPassword", description="旧密码")
    new_password:str = Field(..., min_length=6, alias="newPassword", description="新密码")