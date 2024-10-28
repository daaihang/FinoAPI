import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_apscheduler import APScheduler as _BaseAPScheduler

db = SQLAlchemy()  # 数据库实例
migrate = Migrate()  # 迁移工具实例


class APScheduler(_BaseAPScheduler):
    def run_job(self, id, jobstore=None):
        with self.app.app_context():  # 引入 Flask 上下文
            super().run_job(id=id, jobstore=jobstore)


def create_app():
    app = Flask(__name__)

    # 根据环境变量加载不同的配置
    env = os.getenv('FLASK_ENV', 'development')  # 默认是开发环境
    if env == 'production':
        app.config.from_object('config.production.ProductionConfig')
    else:
        app.config.from_object('config.development.DevelopmentConfig')

    # 初始化数据库和迁移工具
    db.init_app(app)
    migrate.init_app(app, db)

    # 导入所有模型
    with app.app_context():
        from app.models import user, events, base, sms, sensitive_data

        # 初始化调度器
        # scheduler = APScheduler()
        # scheduler.init_app(app)
        #
        # # 导入并添加定时任务
        # from app.services.scheduled import add_jobs
        # add_jobs(scheduler)  # 添加定时任务
        # scheduler.start()

    # 初始化 Flask-Admin
    from app.admin import init_admin
    init_admin(app)

    # 注册所有的 API 路由
    from app.api import register_routes
    register_routes(app)

    return app
