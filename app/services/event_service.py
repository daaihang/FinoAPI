from app.models import Event, Contact
from app import db

from config.base import Config  # 导入配置类

def create_event(event_data):
    """创建一个新活动"""
    event = Event(
        name=event_data['name'],
        start_time=event_data['start_time'],
        end_time=event_data['end_time'],
        registration_start_time=event_data['registration_start_time'],
        registration_end_time=event_data['registration_end_time'],
        max_participants=event_data['max_participants'],
        organizers=event_data['organizers'],
        co_organizers=event_data['co_organizers'],
        location=event_data['location'],
        details=event_data['details'],
        images=event_data['images'],
        registration_review_required=event_data['registration_review_required'],
        registration_required=event_data['registration_required'],
        is_public=event_data['is_public'],
        is_delete=event_data['is_delete']
    )
    db.session.add(event)
    db.session.commit()
    return event


def get_event(event_id):
    """获取单个活动"""
    return Event.query.get(event_id)


def get_all_events(page, per_page):
    """获取所有活动，支持分页"""
    per_page = int(per_page)  # 确保 per_page 是整数
    page = int(page)  # 确保 page 是整数

    # 检查 per_page 是否在允许的分页大小列表中
    if per_page not in Config.PAGE_SIZES:
        per_page = Config.PAGE_SIZES[0]  # 如果不在允许的列表中，使用默认的分页大小

    pagination = Event.query.paginate(page=page, per_page=per_page, error_out=True)
    return pagination.items, pagination.total


def update_event(event_id, updated_data):
    """更新活动信息"""
    event = Event.query.get(event_id)
    if event:
        for key, value in updated_data.items():
            setattr(event, key, value)
        db.session.commit()
    return event


def delete_event(event_id):
    """删除活动"""
    event = Event.query.get(event_id)
    if event:
        db.session.delete(event)
        db.session.commit()
    return event
