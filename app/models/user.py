# app/models/user.py
from app import db
import uuid


class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment='用户唯一ID，UUID')
    username = db.Column(db.String(63), nullable=True, comment='用户名')
    phone_number = db.Column(db.String(63), nullable=True, comment='电话号码')
    email = db.Column(db.String(255), nullable=True, comment='电子邮件地址')
    wechat_openid = db.Column(db.String(63), nullable=True, comment='微信OpenID')
    wechat_unionid = db.Column(db.String(63), nullable=True, comment='微信UnionID')
    password = db.Column(db.String(255), nullable=True, comment='密码')
    session_key = db.Column(db.String(127), nullable=True, comment='微信登录加密密钥')

    def __repr__(self):
        return f'<User {self.user_id}>'

    def to_dict(self):
        """将用户对象转化为字典，方便JSON序列化"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'phone_number': self.phone_number,
            'email': self.email,
            'wechat_openid': self.wechat_openid
        }
