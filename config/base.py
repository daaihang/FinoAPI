import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    FLASK_ENV = os.getenv('FLASK_ENV')

    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 微信小程序的 AppID 和 AppSecret
    WECHAT_APP_ID = os.getenv('WECHAT_APP_ID')
    WECHAT_APP_SECRET = os.getenv('WECHAT_APP_SECRET')

    # 腾讯云 COS 对象存储配置
    COS_SECRET_ID = os.environ.get('COS_SECRET_ID')
    COS_SECRET_KEY = os.environ.get('COS_SECRET_KEY')
    COS_REGION = os.environ.get('COS_REGION', 'ap-guangzhou')
    COS_BUCKET_NAME = os.environ.get('COS_BUCKET_NAME')

    # 其他配置项
    JWT_EXPIRATION_DELTA = 48  # JWT 超时时长，单位为小时
    PAGE_SIZES = [10, 20, 50, 100]  # 允许的每页/每次查询数，避免单次查询过多活动，避免脱裤
    VALID_ROLES = ['root', 'admin', 'user', 'guest']  # 角色列表，需要权限从大到小排

    UNSPLASH_SECRET_KEY = os.getenv('UNSPLASH_SECRET_KEY')

    # 上传文件的路径配置（用户头像、详情页的图片、海报、公告图片、报名表单附件）
    AVATAR_FOLDER = "uploads/avatars"
    DETAILS_FOLDER = "uploads/details"
    POSTER_FOLDER = "uploads/posters"
    ANNOUNCEMENT_FOLDER = "uploads/announcements"
    ATTACHMENT_FOLDER = "uploads/attachments"
