# app/models/user.py
from app import db

import uuid
from werkzeug.security import generate_password_hash, check_password_hash

from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = 'user'

    user_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment='用户唯一ID，UUID')
    username = db.Column(db.String(63), nullable=True, comment='用户名')
    phone_number = db.Column(db.String(63), nullable=True, comment='电话号码')
    email = db.Column(db.String(255), nullable=True, comment='电子邮件地址')
    wechat_openid = db.Column(db.String(63), nullable=True, comment='微信OpenID')
    wechat_unionid = db.Column(db.String(63), nullable=True, comment='微信UnionID')
    password = db.Column(db.String(255), nullable=True, comment='密码')
    session_key = db.Column(db.String(127), nullable=True, comment='微信登录加密密钥')
    role = db.Column(db.String(20), nullable=False, default='guest', comment='用户角色')
    jwt_revoked = db.Column(db.Boolean, default=False, comment='JWT是否已注销')
    avatar = db.Column(db.String(512), nullable=True, comment='用户头像')

    # 关联积分系统和钱包系统
    points = db.relationship('Points', uselist=False, backref='user', cascade='all, delete-orphan')
    wallet = db.relationship('Wallet', uselist=False, backref='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.user_id}>'

    def to_dict(self):
        """将用户对象转化为字典，方便JSON序列化"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'phone_number': self.phone_number,
            'email': self.email,
            'wechat_openid': self.wechat_openid,
            'role': self.role,
            'jwt_revoked': self.jwt_revoked,
            'avatar': self.avatar,
        }

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)


class Points(BaseModel):
    __tablename__ = 'points'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False, comment='用户ID')
    balance = db.Column(db.Integer, nullable=False, default=0, comment='当前积分余额')

    def __repr__(self):
        return f'<Points {self.user_id} - {self.balance}>'


class PointsTransaction(BaseModel):
    __tablename__ = 'points_transaction'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False, comment='用户ID')
    change_amount = db.Column(db.Integer, nullable=False, comment='积分变化数')
    description = db.Column(db.String(255), comment='交易描述')

    def __repr__(self):
        return f'<PointsTransaction {self.user_id} - {self.change_amount}>'


class Wallet(BaseModel):
    __tablename__ = 'wallet'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False, comment='用户ID')
    balance = db.Column(db.Float, nullable=False, default=0.0, comment='钱包余额')

    def __repr__(self):
        return f'<Wallet {self.user_id} - {self.balance}>'


class WalletTransaction(BaseModel):
    __tablename__ = 'wallet_transaction'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False, comment='用户ID')
    amount = db.Column(db.Float, nullable=False, comment='交易金额')
    transaction_type = db.Column(db.String(50), comment='交易类型，如充值、消费')
    description = db.Column(db.String(255), comment='交易描述')

    def __repr__(self):
        return f'<WalletTransaction {self.user_id} - {self.amount}>'
