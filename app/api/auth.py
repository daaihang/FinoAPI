from flask import Blueprint, request, jsonify

from app.services.auth_service import wechat_login, get_all_users, get_user_info
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
@jwt_required("admin")
def get_user(openid):
    """根据 OpenID 获取用户信息"""
    return get_user_info(openid)


@bp.route('/protected', methods=['GET'])
@jwt_required("admin", "editor")  # 多个角色
def protected():
    return jsonify({'message': 'Welcome Admin or Editor'}), 200
