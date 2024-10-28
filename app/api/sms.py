from flask import Blueprint, request, jsonify, g

from app.services.sms_service import send_verification_code, validate_frequent_send, verify_sms_code
from app.services.decorators import jwt_required  # 导入装饰器

bp = Blueprint('sms_bp', __name__)


# 发送验证码
@bp.route('/send_code', methods=['POST'])
@jwt_required()
def send_code():
    phone_number = request.json.get('phone_number')
    user_id = g.current_user.user_id
    if not phone_number:
        return jsonify({'error': 'Invalid input'}), 400

    # 检查发送频率
    if not validate_frequent_send(user_id, phone_number):
        return jsonify({'error': 'Too many requests'}), 429

    # 发送验证码并存入数据库
    result = send_verification_code(user_id, phone_number)
    if result['success']:
        return jsonify({'message': 'Verification code sent successfully'})
    else:
        return jsonify({'error': result['error']}), 500


# 验证验证码
@bp.route('/verify_code', methods=['POST'])
@jwt_required()
def verify_code():
    """
    当前的验证逻辑不需要路由代码，而是直接调用逻辑函数。未使用到当前函数。
    :return:
    """
    user_id = g.current_user.user_id
    phone_number = request.json.get('phone_number')
    code = request.json.get('code')
    if verify_sms_code(user_id, phone_number, code):
        return jsonify({'message': 'Verification and commit successful'})
    else:
        return jsonify({'error': 'Invalid or expired code'}), 400
