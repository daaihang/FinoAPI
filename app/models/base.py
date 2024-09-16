from app import db
import datetime


class BaseModel(db.Model):
    __abstract__ = True  # 这是一个抽象模型类，不会创建表

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=True, comment='记录创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=True, comment='记录更新时间')

    def save(self):
        """保存对象到数据库"""
        if not self.created_at:
            self.created_at = datetime.datetime.utcnow()
        if not self.updated_at:
            self.updated_at = datetime.datetime.utcnow()
        db.session.add(self)
        db.session.commit()