from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from schemas.base import NewsItemBase


class FavoriteCheckResponse(BaseModel):
    is_favorite: bool = Field(..., alias="isFavorite")

class FavoriteAddRequest(BaseModel):
    news_id: int = Field(..., alias="newsId")

# 规划两个类: 一个是新闻模型类(后续浏览历史有用) + 收藏的模型类
class FavoriteNewsItemResponse(NewsItemBase):
    favorite_id: int = Field(alias="favoriteId")
    favorite_time: datetime = Field(alias="favoriteTime")

    model_config = ConfigDict(
        populate_by_name=True,  # 别名和字段名兼容
        from_attributes=True  # 允许从ORM模型类中提取属性值
    )

# 收藏列表接口响应模型类
class FavoriteListResponse(BaseModel):
    list: list[FavoriteNewsItemResponse]
    total: int = Field(..., alias="total")
    has_more: bool = Field(alias="hasMore")

    model_config = ConfigDict(
        populate_by_name=True,  # 别名和字段名兼容
        from_attributes=True    # 允许从ORM模型类中提取属性值
    )