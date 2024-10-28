import uuid
from app import db
from app.models.base import BaseModel

import pytz

class Event(BaseModel):
    __tablename__ = 'events'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment='活动唯一ID，UUID')
    name = db.Column(db.String(255), nullable=False, comment='活动名称')
    create_user = db.Column(db.String(36), db.ForeignKey('user.user_id'), nullable=True,
                            comment='创建该活动的用户，外键')
    start_time = db.Column(db.DateTime, nullable=False, comment='活动开始时间')
    end_time = db.Column(db.DateTime, nullable=False, comment='活动结束时间')
    registration_start_time = db.Column(db.DateTime, nullable=True, comment='报名开始时间')
    registration_end_time = db.Column(db.DateTime, nullable=True, comment='报名结束时间')
    max_participants = db.Column(db.Integer, nullable=False, comment='最大报名人数')
    organizers = db.Column(db.Text, nullable=True, comment='活动主办单位')
    co_organizers = db.Column(db.Text, nullable=True, comment='活动承办单位')
    location = db.Column(db.String(255), nullable=True, comment='活动名称')
    address = db.Column(db.String(255), nullable=True, comment='活动地点（省市区门牌号的详细描述）')
    details = db.Column(db.Text, nullable=True, comment='活动详情（Markdown 文件的地址）')
    image = db.Column(db.Text, nullable=True, comment='活动图片海报（URL）')
    registration_review_required = db.Column(db.Boolean, nullable=False, default=False, comment='报名是否需要审核')
    registration_required = db.Column(db.Boolean, nullable=False, default=True, comment='活动是否需要报名')
    is_public = db.Column(db.Boolean, nullable=False, default=False, comment='活动是否发布、公开')
    is_delete = db.Column(db.Boolean, nullable=False, default=False, comment='活动是否归档、删除')
    tags = db.Column(db.Text, nullable=True, comment='活动标签，英文逗号分隔的无空格字符串')
    type = db.Column(db.String(32), nullable=False, default='activity', comment='活动类型(exhibition展览/activity活动)')

    # todo: 新增场次字段（字典），报名时有不同的场次选择。

    # Relationships
    contacts = db.relationship('Contact', backref='event', cascade='all, delete-orphan')

    def __init__(self, name, create_user, start_time, end_time, registration_start_time, registration_end_time, max_participants,
                 organizers, co_organizers, location, address, details, image, registration_review_required,
                 registration_required, is_public, is_delete, tags, type):
        self.name = name
        self.create_user = create_user
        self.start_time = start_time
        self.end_time = end_time
        self.registration_start_time = registration_start_time
        self.registration_end_time = registration_end_time
        self.max_participants = max_participants
        self.organizers = organizers
        self.co_organizers = co_organizers
        self.location = location
        self.address = address
        self.details = details
        self.image = image
        self.registration_review_required = registration_review_required
        self.registration_required = registration_required
        self.is_public = is_public
        self.is_delete = is_delete
        self.tags = tags
        self.type = type

    def __repr__(self):
        return f'<Event {self.name} (ID: {self.id})>'

    def to_dict(self):
        """将活动对象转化为字典，方便JSON序列化"""

        # 定义东八区时区
        tz = pytz.timezone('Asia/Shanghai')

        def format_time(dt):
            """辅助函数，将时间转化为东八区的 YYYY-MM-DD hh:mm:ss 格式"""
            if dt:
                # 将时间转为东八区并格式化
                dt_utc = dt.astimezone(tz)
                return dt_utc.strftime('%Y-%m-%d %H:%M:%S')
            return None

        return {
            'id': self.id,
            'name': self.name,
            'create_user': self.create_user,
            'start_time': format_time(self.start_time),
            'end_time': format_time(self.end_time),
            'registration_start_time': format_time(self.registration_start_time),
            'registration_end_time': format_time(self.registration_end_time),
            'max_participants': self.max_participants,
            'organizers': self.organizers,
            'co_organizers': self.co_organizers,
            'location': self.location,
            'address': self.address,
            'details': self.details,
            'image': self.image,
            'registration_review_required': self.registration_review_required,
            'registration_required': self.registration_required,
            'is_public': self.is_public,
            'is_delete': self.is_delete,
            'tags': self.tags,
            'type': self.type
        }


# Contact 会被 Event 引用，因此不用单独导入，会跟着 Event 导入(?存疑)
class Contact(BaseModel):
    __tablename__ = 'contacts'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment='联系人唯一ID，UUID')
    event_id = db.Column(db.String(36), db.ForeignKey('events.id'), nullable=False, comment='活动ID，外键')
    name = db.Column(db.String(255), nullable=False, comment='联系人姓名')
    channel = db.Column(db.String(50), nullable=False, comment='联系方式渠道（电话、微信、邮箱等）')
    value = db.Column(db.String(255), nullable=False, comment='联系方式的值')

