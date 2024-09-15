import uuid
from app import db


class Event(db.Model):
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
    registration_review_required = db.Column(db.Boolean, default=False, comment='报名是否需要审核')
    registration_required = db.Column(db.Boolean, default=True, comment='活动是否需要报名')

    # Relationships
    contacts = db.relationship('Contact', backref='event', cascade='all, delete-orphan')

    def __init__(self, name, start_time, end_time, registration_start_time, registration_end_time, max_participants,
                 organizers, co_organizers, location, details, images, registration_review_required,
                 registration_required):
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


class Contact(db.Model):
    __tablename__ = 'contacts'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment='联系人唯一ID，UUID')
    event_id = db.Column(db.String(36), db.ForeignKey('events.id'), nullable=False, comment='活动ID，外键')
    name = db.Column(db.String(255), nullable=False, comment='联系人姓名')
    channel = db.Column(db.String(50), nullable=False, comment='联系方式渠道（电话、微信、邮箱等）')
    value = db.Column(db.String(255), nullable=False, comment='联系方式的值')

