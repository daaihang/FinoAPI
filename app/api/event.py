from flask import Blueprint, request, jsonify
from app.services.event_service import create_event, get_event, get_all_events, update_event, delete_event

from app.services.decorators import jwt_required  # 导入装饰器


bp = Blueprint('event', __name__)


@bp.route('/new', methods=['POST'])
@jwt_required("admin")
def create_event_route():
    """创建新活动"""
    event_data = request.json
    event = create_event(event_data)
    return jsonify(event.to_dict()), 201


@bp.route('/<event_id>', methods=['GET'])
@jwt_required("admin")
def get_event_route(event_id):
    """获取单个活动"""
    event = get_event(event_id)
    if event:
        return jsonify(event.to_dict()), 200
    return jsonify({'message': 'Event not found'}), 404


@bp.route('/all_events', methods=['GET'])
@jwt_required("admin")
def get_all_events_route():
    """获取所有活动，支持分页"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    events, total = get_all_events(page, per_page)
    return jsonify({
        'total': total,
        'events': [event.to_dict() for event in events],
        'page': page,
        'per_page': per_page
    }), 200


@bp.route('/<event_id>', methods=['PUT'])
@jwt_required("admin")
def update_event_route(event_id):
    """更新活动信息"""
    updated_data = request.json
    event = update_event(event_id, updated_data)
    if event:
        return jsonify(event.to_dict()), 200
    return jsonify({'message': 'Event not found'}), 404


@bp.route('/<event_id>', methods=['DELETE'])
def delete_event_route(event_id):
    """删除活动"""
    event = delete_event(event_id)
    if event:
        return jsonify({'message': 'Event deleted successfully'}), 200
    return jsonify({'message': 'Event not found'}), 404