import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # 数据库迁移工具

from app.api import register_routes


db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # 根据环境变量加载不同的配置
    env = os.getenv('FLASK_ENV', 'development')  # 默认是开发环境
    if env == 'production':
        app.config.from_object('config.production.ProductionConfig')
    else:
        app.config.from_object('config.development.DevelopmentConfig')

    # 初始化数据库
    db.init_app(app)
    migrate.init_app(app, db)

    # 导入所有模型
    with app.app_context():
        # 导入模型模块
        from app.models import user, events, base, sms
        # 可以在这里导入其他模型模块，有新模型需要及时在此加上
        # from app.models import other_model

    # 注册所有的 API 路由
    register_routes(app)

    return app
