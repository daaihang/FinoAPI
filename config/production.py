import os

from .base import Config

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')

    # 生产环境的微信服务器接口地址
    WECHAT_API_URL = 'https://api.weixin.qq.com/sns/jscode2session'
