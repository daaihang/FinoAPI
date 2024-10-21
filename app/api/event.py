from flask import Blueprint, request, jsonify
from app.services.event_service import create_event, get_event, get_all_events, update_event, delete_event

from app.services.decorators import jwt_required  # 导入装饰器


bp = Blueprint('event', __name__)


@bp.route('/new', methods=['POST'])
@jwt_required("admin", "monitor")
def create_event_route():
    """创建新活动"""
    event_data = request.json
    event = create_event(event_data)
    return jsonify(event.to_dict()), 201


@bp.route('/<event_id>', methods=['GET'])
@jwt_required("admin", "monitor")
def get_event_route(event_id):
    """获取单个活动"""
    event = get_event(event_id)
    if event:
        return jsonify(event.to_dict()), 200
    return jsonify({'message': 'Event not found'}), 404


@bp.route('/all_events', methods=['GET'])
@jwt_required()
def get_all_events_route():
    """获取所有活动，支持类型过滤、排序、分页和活动筛选"""
    # 获取参数
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    event_type = request.args.get('type', 'all')  # 活动类型，默认为 'all'
    sort_by = request.args.get('sort_by', 'start_time')  # 排序字段，默认为 'start_time'
    sort_order = request.args.get('sort_order', 'asc')  # 排序顺序，默认为升序
    filter_status = request.args.get('filter_status', 'none')  # 筛选状态

    # 检查必要参数
    if per_page <= 0:
        return jsonify({'error': '每页数量必须大于0'}), 400
    if page <= 0:
        return jsonify({'error': '页码必须大于0'}), 400
    if sort_order not in ['asc', 'desc']:
        return jsonify({'error': '无效的排序顺序，必须是 "asc" 或 "desc"'}), 400
    if filter_status not in ['none', 'not_started_registration', 'ongoing_registration', 'ended_registration',
                             'not_started', 'ongoing', 'ended']:
        return jsonify({'error': '无效的筛选状态'}), 400

    # 获取活动列表
    events, total = get_all_events(page, per_page, event_type, sort_by, sort_order, filter_status)

    return jsonify({
        'total': total,
        'events': [event.to_dict() for event in events],
        'page': page,
        'per_page': per_page
    }), 200


@bp.route('/<event_id>', methods=['PUT'])
@jwt_required("admin", "monitor")
def update_event_route(event_id):
    """更新活动信息"""
    updated_data = request.json
    event = update_event(event_id, updated_data)
    if event:
        return jsonify(event.to_dict()), 200
    return jsonify({'message': 'Event not found'}), 404


@bp.route('/<event_id>', methods=['DELETE'])
@jwt_required("admin", "monitor")
def delete_event_route(event_id):
    """删除活动"""
    event = delete_event(event_id)
    if event:
        return jsonify({'message': 'Event deleted successfully'}), 200
    return jsonify({'message': 'Event not found'}), 404