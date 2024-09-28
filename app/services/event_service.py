from datetime import datetime

from app.models import Event, Contact
from app import db

from sqlalchemy import and_

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
        image=event_data['image'],
        registration_review_required=event_data['registration_review_required'],
        registration_required=event_data['registration_required'],
        is_public=event_data['is_public'],
        is_delete=event_data['is_delete'],
        tags=event_data['tags'],
        type=event_data['type']
    )
    db.session.add(event)
    db.session.commit()
    return event


def get_event(event_id):
    """获取单个活动"""
    return Event.query.get(event_id)


def get_all_events(page, per_page, event_type, sort_by, sort_order, filter_status):
    """获取所有活动或某类型活动，支持分页、排序、过滤"""
    query = Event.query

    # 按类型过滤
    if event_type != 'all':
        query = query.filter_by(type=event_type)

    # 筛选状态
    current_time = datetime.now()
    if filter_status == 'not_started_registration':
        query = query.filter(Event.registration_start_time > current_time)
    elif filter_status == 'ongoing_registration':
        query = query.filter(and_(Event.registration_start_time <= current_time, Event.registration_end_time > current_time))
    elif filter_status == 'ended_registration':
        query = query.filter(Event.registration_end_time < current_time)
    elif filter_status == 'not_started':
        query = query.filter(Event.start_time > current_time)
    elif filter_status == 'ongoing':
        query = query.filter(and_(Event.start_time <= current_time, Event.end_time > current_time))
    elif filter_status == 'ended':
        query = query.filter(Event.end_time < current_time)

    # 排序
    if sort_by == 'start_time':
        if sort_order == 'asc':
            query = query.order_by(Event.start_time.asc())
        else:
            query = query.order_by(Event.start_time.desc())
    elif sort_by == 'registration_end_time':
        if sort_order == 'asc':
            query = query.order_by(Event.registration_end_time.asc())
        else:
            query = query.order_by(Event.registration_end_time.desc())

    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=True)
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
