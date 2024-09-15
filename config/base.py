import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 微信小程序的 AppID 和 AppSecret
    WECHAT_APP_ID = os.getenv('WECHAT_APP_ID')
    WECHAT_APP_SECRET = os.getenv('WECHAT_APP_SECRET')

    # 其他配置项
    JWT_EXPIRATION_DELTA = 48  # JWT 超时时长，单位为小时
