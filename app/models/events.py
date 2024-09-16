import uuid
from app import db
from app.models.base import BaseModel


class Event(BaseModel):
    __tablename__ = 'events'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment='活动唯一ID，UUID')
    name = db.Column(db.String(255), nullable=False, comment='活动名称')
    start_time = db.Column(db.DateTime, nullable=False, comment='活动开始时间')
    end_time = db.Column(db.DateTime, nullable=False, comment='活动结束时间')
    registration_start_time = db.Column(db.DateTime, nullable=True, comment='报名开始时间')
    registration_end_time = db.Column(db.DateTime, nullable=True, comment='报名结束时间')
    max_participants = db.Column(db.Integer, nullable=False, comment='最大报名人数')
    organizers = db.Column(db.Text, nullable=True, comment='活动主办单位')
    co_organizers = db.Column(db.Text, nullable=True, comment='活动承办单位')
    location = db.Column(db.String(255), nullable=True, comment='活动地点')
    details = db.Column(db.Text, nullable=True, comment='活动详情（Markdown 格式）')
    images = db.Column(db.Text, nullable=True, comment='活动图片海报（URL 列表）')
    registration_review_required = db.Column(db.Boolean, nullable=False, default=False, comment='报名是否需要审核')
    registration_required = db.Column(db.Boolean, nullable=False, default=True, comment='活动是否需要报名')
    is_public = db.Column(db.Boolean, nullable=False, default=False, comment='活动是否发布、公开')
    is_delete = db.Column(db.Boolean, nullable=False, default=False, comment='活动是否归档、删除')

    # Relationships
    contacts = db.relationship('Contact', backref='event', cascade='all, delete-orphan')

    def __init__(self, name, start_time, end_time, registration_start_time, registration_end_time, max_participants,
                 organizers, co_organizers, location, details, images, registration_review_required,
                 registration_required, is_public, is_delete):
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.registration_start_time = registration_start_time
        self.registration_end_time = registration_end_time
        self.max_participants = max_participants
        self.organizers = organizers
        self.co_organizers = co_organizers
        self.location = location
        self.details = details
        self.images = images
        self.registration_review_required = registration_review_required
        self.registration_required = registration_required
        self.is_public = is_public
        self.is_delete = is_delete

    def __repr__(self):
        return f'<Event {self.name} (ID: {self.id})>'

    def to_dict(self):
        """将活动对象转化为字典，方便JSON序列化"""
        return {
            'id': self.id,
            'name': self.name,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'registration_start_time': self.registration_start_time.isoformat() if self.registration_start_time else None,
            'registration_end_time': self.registration_end_time.isoformat() if self.registration_end_time else None,
            'max_participants': self.max_participants,
            'organizers': self.organizers,
            'co_organizers': self.co_organizers,
            'location': self.location,
            'details': self.details,
            'images': self.images,
            'registration_review_required': self.registration_review_required,
            'registration_required': self.registration_required,
            'is_public': self.is_public,
            'is_delete': self.is_delete
        }


# Contact会被Event引用，因此不用单独导入，会跟着Event导入
class Contact(BaseModel):
    __tablename__ = 'contacts'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment='联系人唯一ID，UUID')
    event_id = db.Column(db.String(36), db.ForeignKey('events.id'), nullable=False, comment='活动ID，外键')
    name = db.Column(db.String(255), nullable=False, comment='联系人姓名')
    channel = db.Column(db.String(50), nullable=False, comment='联系方式渠道（电话、微信、邮箱等）')
    value = db.Column(db.String(255), nullable=False, comment='联系方式的值')

