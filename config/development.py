import os

from .base import Config

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

    # 本地微信服务器接口地址
    WECHAT_API_URL = 'https://api.weixin.qq.com/sns/jscode2session'
