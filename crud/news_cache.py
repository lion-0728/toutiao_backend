from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, and_, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from cache.news_cache import get_cached_categories, set_cache_categories, get_cache_news_list, set_cache_news_list
from models.news import Category, News
from schemas.base import NewsItemBase


async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    # 先尝试从缓存中获取数据
    cached_categories = await get_cached_categories()
    if cached_categories:
        return cached_categories

    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    categories = result.scalars().all()   # ORM 模型对象

    # 写入缓存
    if categories:
        categories = jsonable_encoder(categories)  # 将ORM对象转换为JSON对象
        await set_cache_categories(categories)

    # 返回数据
    return categories

async def get_news_list(db: AsyncSession, category_id: int, skip: int = 0, limit: int = 10):
    # 先尝试从缓存获取新闻列表
    # 跳过的数量skip = (页码 -1) * 每页数量 → 页码 = 跳过的数量 // 每页数量 + 1
    # await get_cache_news_list(分类id, 页码, 每页数量)
    page = skip // limit + 1
    cached_list = await get_cache_news_list(category_id, page, limit)  # 缓存数据 json
    if cached_list:
        # return cached_list  # 要的是 ORM
        return [News(**item) for item in cached_list]

    # 查询的是指定分类下的所有新闻 将 News.category_id == category_id 包装在 and_() 函数中，这样可以明确告诉类型检查器这是一个 SQL 表达式，而不是普通的 Python bool
    # 值这种写法可以解决类型检查器的推断问题，同时在功能上完全等价于原来的代码。
    stmt = select(News).where(and_(News.category_id == category_id)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    news_list =  result.scalars().all()

    # 写入缓存
    if news_list:
        # 先把 ORM 数据 转换 字典才能写入缓存
        # ORM 转成 Pydantic，再转为 字典
        # by_alias=False 不适用别名，保存 Python 风格，因为 Redis 数据是给后端用的
        news_data = [NewsItemBase.model_validate(item).model_dump(mode="json", by_alias=False) for item in news_list]
        await set_cache_news_list(category_id, page, limit, news_data)

    return news_list



async def get_news_count(db: AsyncSession, category_id: int):
    # 查询的是指定分类下的新闻数量
    stmt = select(func.count(News.id)).where(and_(News.category_id == category_id))
    result = await db.execute(stmt)
    return result.scalar_one()  # 只能有一个结果,否则报错

async def get_news_detail(db: AsyncSession, news_id: int):
    stmt = select(News).where(and_(News.id == news_id))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()  # 获取一个结果或者找不到返回none

async def increase_news_views(db: AsyncSession, news_id: int):
    stmt = update(News).where(and_(News.id == news_id)).values(views=News.views + 1)
    result = await db.execute(stmt)
    await db.commit()  # db_conf.py下的依赖项是当前会话操作都执行完才会执行commit操作,以防万一,这里加一个commit操作

    # 更新 -> 检查数据库是否真的命中了数据 -> 命中了返回True
    return result.rowcount > 0

async def get_related_news(db: AsyncSession, news_id: int, category_id: int, limit: int = 5):
    # order_by 排序 -> 浏览量和发布时间
    stmt = select(News).where(
        and_(News.id != news_id,
             News.category_id == category_id)
    ).order_by(
        News.views.desc(),  # 默认是升序,desc表示降序
        News.publish_time.desc()  # 时间降序
    ).limit(limit)
    result = await db.execute(stmt)
    # return result.scalars().all()
    related_news = result.scalars().all()
    # 列表推导式 推导出新闻的核心数据,然后再return
    return [{
        "id": news_detail.id,
        "title": news_detail.title,
        "content": news_detail.content,
        "image": news_detail.image,
        "author": news_detail.author,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
        "views": news_detail.views
    } for news_detail in related_news]