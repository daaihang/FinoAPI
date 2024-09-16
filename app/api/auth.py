from flask import Blueprint, request, jsonify
import jwt

from app.services.auth_service import wechat_login, get_all_users, get_user_info, update_user_role
from app.services.decorators import jwt_required  # 导入装饰器

from config.base import Config

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['POST'])
def login():
    """微信小程序登录"""
    code = request.json.get('code')
    if not code:
        return jsonify({'error': 'Code is required'}), 400
    return wechat_login(code)


@bp.route('/users', methods=['GET'])
@jwt_required("admin")
def list_users():
    """获取所有用户"""
    return get_all_users()


@bp.route('/user/<openid>', methods=['GET'])
@jwt_required("root")
def get_user(openid):
    """根据 OpenID 获取用户信息"""
    return get_user_info(openid)


@bp.route('/protected', methods=['GET'])
@jwt_required("admin", "editor")  # 多个角色
def protected():
    """测试用的路由，测试权限代码"""
    return jsonify({'message': 'Welcome Admin or Editor'}), 200


@bp.route('/update_role', methods=['POST'])
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
