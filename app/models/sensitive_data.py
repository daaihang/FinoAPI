import uuid
from app import db
from app.models.base import BaseModel


class SensitiveData(BaseModel):
    __tablename__ = 'sensitive_data'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment='记录唯一ID，UUID')
    key_name = db.Column(db.String(255), nullable=False, unique=True, comment='键的名称，例如access_token、api_key等')
    key_value = db.Column(db.String(1024), nullable=False, comment='存储的敏感数据值，例如access_token')
    expires_in = db.Column(db.Integer, nullable=True, comment='过期时间，以秒为单位')

    def __init__(self, key_name, key_value, expires_in=None):
        self.key_name = key_name
        self.key_value = key_value
        self.expires_in = expires_in

    def __repr__(self):
        return (f'<SensitiveData KeyName: {self.key_name}, '
                f'Expires In: {self.expires_in if self.expires_in else "No Expiry"}>')

    def to_dict(self):
        """将敏感数据对象转化为字典，方便JSON序列化"""
        return {
            'id': self.id,
            'key_name': self.key_name,
            'key_value': self.key_value,
            'expires_in': self.expires_in
        }

    def is_expired(self):
        """检查记录是否已经过期"""
        if self.expires_in:
            elapsed_time = (db.func.now() - self.created_at).total_seconds()
            return elapsed_time >= self.expires_in
        return False
