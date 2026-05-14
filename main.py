from fastapi import FastAPI
from routers import news, users, favorite, history
from fastapi.middleware.cors import CORSMiddleware

from utils.exception_handlers import register_exception_handlers

app = FastAPI()

# noinspection PyTypeChecker
# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # 允许的源,开发阶段允许所有源,生产环境需要指定源
    allow_credentials=True,     # 允许携带cookie
    allow_methods=["*"],        # 允许的请求方法
    allow_headers=["*"],        # 允许的请求头
)

# 注册异常处理器
register_exception_handlers(app)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

# 挂载路由/注册路由  在main.py里面引入路由模块,依赖于fastapi实例
app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
app.include_router(history.router)
