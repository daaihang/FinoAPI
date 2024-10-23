import uuid
from app import db
from app.models.base import BaseModel


class SmsRecord(BaseModel):
    __tablename__ = 'sms_records'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment='记录唯一ID，UUID')
    user_id = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=False, comment='用户ID，外键')
    sms_type = db.Column(db.String(50), nullable=False, comment='短信类型（验证码verification、通知等）')
    phone = db.Column(db.String(16), nullable=False, comment='接收短信的手机号')
    contact = db.Column(db.String(50), nullable=True, comment='短信内容，若是验证码应只写验证码的4-8位数字')
    status = db.Column(db.Boolean, nullable=False, comment='发送状态，True为成功，False为失败')

    # Relationships
    user = db.relationship('User', backref='sms_records')

    def __init__(self, user_id, sms_type, phone, contact=None, status=False):
        self.user_id = user_id
        self.sms_type = sms_type
        self.phone = phone
        self.contact = contact
        self.status = status

    def __repr__(self):
        return (f'<SmsRecord UserID: {self.user_id}, Type: {self.sms_type}, '
                f'Status: {"Success" if self.status else "Failure"}>, Contact: {self.contact}')

    def to_dict(self):
        """将短信记录对象转化为字典，方便JSON序列化"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'sms_type': self.sms_type,
            'phone': self.phone,
            'contact': self.contact,
            'status': 'Success' if self.status else 'Failure'
        }
