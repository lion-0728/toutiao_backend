from sqlalchemy import select, and_, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.news import Category, News


async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_news_list(db: AsyncSession, category_id: int, skip: int = 0, limit: int = 10):
    # 查询的是指定分类下的所有新闻 将 News.category_id == category_id 包装在 and_() 函数中，这样可以明确告诉类型检查器这是一个 SQL 表达式，而不是普通的 Python bool
    # 值这种写法可以解决类型检查器的推断问题，同时在功能上完全等价于原来的代码。
    stmt = select(News).where(and_(News.category_id == category_id)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

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