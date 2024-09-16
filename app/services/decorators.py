import jwt
from functools import wraps
from flask import request, jsonify, g
from config.base import Config
from app.models import User  # 假设您有一个用户模型

def jwt_required(*required_roles):
    """装饰器用于验证 JWT 并检查用户角色。更改用户角色后需要重新获取新的JWT避免验证失败。

    :param required_roles: 需要的角色列表，如果不传则默认接受所有角色
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 直接获取 Authorization 请求头中的 token
            token = request.headers.get('Authorization', None)

            if not token:
                return jsonify({'message': 'Token is missing!'}), 401

            try:
                # 解码 token
                secret_key = Config.SECRET_KEY
                decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
                user_id = decoded_token.get('user_id')
                user_role = decoded_token.get('role')

                if not user_id or not user_role:
                    return jsonify({'message': 'Token is invalid!'}), 401

                # 查询用户
                current_user = User.query.filter_by(user_id=user_id).first()

                if not current_user:
                    return jsonify({'message': 'User not found!'}), 401

                # 检查 JWT 是否被标记为无效
                if current_user.jwt_revoked:
                    return jsonify({'message': 'Token has been revoked, please log in again!'}), 401

                # 角色验证
                if required_roles and user_role not in required_roles:
                    return jsonify({'message': 'Permission denied!'}), 403

                # 将当前用户存储在全局对象 g 中，供视图函数使用
                g.current_user = current_user

            except jwt.ExpiredSignatureError:  # JWT 过期
                return jsonify({'message': 'Token has expired!'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'message': 'Invalid token!'}), 401

            return f(*args, **kwargs)

        return decorated_function

    return decorator
