from flask import Blueprint, request, jsonify, g, send_file
import jwt

from app.services.auth_service import (wechat_login, get_all_users, get_user_info, update_user_role,
                                       get_user_self_info, bind_phone, generate_user_qr_code, get_padded_secret_key,
                                       decrypt_qr_code_data)
from app.services.decorators import jwt_required  # 导入装饰器

from config.base import Config

bp = Blueprint('auth_bp', __name__)


@bp.route('/login', methods=['POST'])
def login():
    """微信小程序登录"""
    code = request.json.get('code')
    if not code:
        return jsonify({'error': 'Code is required'}), 400
    return wechat_login(code)


@bp.route('/users', methods=['GET'])
@jwt_required("admin", "monitor")
def list_users():
    """获取所有用户"""
    return get_all_users()


@bp.route('/user/<openid>', methods=['GET'])
@jwt_required("admin", "monitor")
def get_user(openid):
    """根据 OpenID 获取用户信息"""
    # print(g.current_user)
    return get_user_info(openid)


@bp.route('/myinfo', methods=['GET'])
@jwt_required()
def get_self_user():
    """根据用户登录令牌 JWT 获取用户自身的信息"""
    # print(g.current_user)
    return get_user_self_info(g.current_user)


@bp.route('/protected', methods=['GET'])
@jwt_required("admin", "monitor")  # 多个角色
def protected():
    """测试用的路由，测试权限代码"""
    return jsonify({'message': 'Welcome Admin or Editor'}), 200


@bp.route('/update_role', methods=['POST'])
@jwt_required("admin", "monitor")
def update_role():
    data = request.get_json()
    user_id = data.get('user_id')
    new_role = data.get('new_role')

    if not user_id or not new_role:
        return jsonify({'error': 'User ID and new role are required'}), 400

    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'error': 'Authorization header is required'}), 401

    try:
        token = auth_header
        decoded_token = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        caller_role = decoded_token.get('role')

        if not caller_role:
            return jsonify({'error': 'Invalid token'}), 401

        update_user_role(caller_role, user_id, new_role)
        return jsonify({'message': 'Role updated successfully'}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/bind_phone', methods=['POST'])
@jwt_required()
def bind_phone_number():
    """
    绑定手机号
    :return:
    """
    user_id = g.current_user.user_id
    phone_number = request.json.get('phone_number')
    code = request.json.get('code')
    return bind_phone(user_id, phone_number, code)


@bp.route('/qr_code', methods=['GET'])
@jwt_required()
def generate_qr_code_route():
    """路由函数：生成并返回用户身份二维码"""
    # 获取用户身份信息（假设通过请求头传递，或其他方式）
    # user_id = request.args.get('user_id')
    user_id = g.current_user.user_id
    if not user_id:
        return jsonify({"error": "Missing user ID"}), 400

    # 调用逻辑函数生成二维码
    img_base64 = generate_user_qr_code(user_id)

    # 返回 Base64 编码的二维码数据
    return jsonify({"qr_code": img_base64}), 200


@bp.route('/decrypt_qr_code', methods=['POST'])
def decrypt_qr_code_route():
    """解密二维码数据并返回时间戳和用户 ID"""
    encrypted_data = request.json.get('encrypted_data')
    if not encrypted_data:
        return jsonify({"error": "Missing encrypted data"}), 400

    try:
        decrypted_data = decrypt_qr_code_data(encrypted_data)
        return jsonify(decrypted_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
