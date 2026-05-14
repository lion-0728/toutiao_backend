from datetime import datetime

from sqlalchemy import select, and_, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.history import History
from models.news import News

# 添加浏览历史记录
async def add_history(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    query = select(History).where(and_(History.user_id == user_id,History.news_id == news_id))
    result = await db.execute(query)
    # 是否存在历史记录
    exiting_history = result.scalar_one_or_none()
    # 如果存在,则更新时间
    if exiting_history:
        exiting_history.view_time = datetime.now()
        await db.commit()
        await db.refresh(exiting_history)
        return exiting_history
    # 如果不存在,则添加
    else:
        history = History(user_id=user_id,news_id=news_id)
        db.add(history)
        await db.commit()
        await db.refresh(history)
        return history

# 获取浏览历史列表: 获取的是某个用户的浏览历史列表 + 分页功能
async def get_history_list(
        db: AsyncSession,
        user_id: int,
        page: 1,
        page_size: 10
):
    # 浏览总量 + 浏览的新闻列表
    count_query = select(func.count(History.id)).where(and_(History.user_id == user_id))
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()
    offset = (page - 1) * page_size

    query = (select(News, History.view_time.label("view_time"), History.id.label("history_id"))
             .join(History, History.news_id == News.id)
             .where(and_(History.user_id == user_id))
             .order_by(History.view_time.desc())
             .offset(offset).limit(page_size)
             )
    result = await db.execute(query)
    rows = result.all()
    return rows, total

# 删除历史记录
async def delete_history(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    # query = select(...)存储的是查询语句对象
    # SELECT 查询：可以用 query 或 stmt
    query = delete(History).where(and_(History.user_id == user_id, History.news_id == news_id))
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0

# 清空历史记录
async def clear_history(
        db: AsyncSession,
        user_id: int
):
    # stmt = delete(...) 存储的是删除语句对象
    # DELETE/UPDATE/INSERT 操作：强烈推荐用 stmt，因为它们不是 "查询"
    stmt = delete(History).where(and_(History.user_id == user_id))
    result = await db.execute(stmt)
    await db.commit()

    return result.rowcount or 0