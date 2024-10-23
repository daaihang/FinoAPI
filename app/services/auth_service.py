import datetime
import os

import jwt
import requests
import json
from flask import jsonify, g
from app.models import User
from app import db
from app.services.sms_service import verify_sms_code
from config.base import Config  # 导入配置类

# 从环境变量获取 AppID 和 AppSecret
WECHAT_APP_ID = Config.WECHAT_APP_ID
WECHAT_APP_SECRET = Config.WECHAT_APP_SECRET
SECRET_KEY = Config.SECRET_KEY

# JWT 过期时间
JWT_EXPIRATION_DELTA = Config.JWT_EXPIRATION_DELTA

# 定义角色级别
ROLE_LEVEL = {role: idx for idx, role in enumerate(Config.VALID_ROLES)}


def get_wechat_session_info(code):
    """根据临时登录凭证 code 调用微信接口获取用户信息"""
    url = 'https://api.weixin.qq.com/sns/jscode2session'
    print("Code: ", code)
    params = {
        'appid': WECHAT_APP_ID,
        'secret': WECHAT_APP_SECRET,
        'js_code': code,
        'grant_type': 'authorization_code'
    }
    response = requests.get(url, params=params)
    return response.json()


def save_user_info(user_info):
    """保存用户信息到数据库"""
    # 从 user_info 中获取 openid
    openid = user_info.get('openid')
    if not openid:
        raise ValueError("用户信息中缺少 'openid'")

    # 查询用户是否存在
    user = User.query.filter_by(wechat_openid=openid).first()

    if user:
        # 更新现有用户的信息
        user.wechat_unionid = user_info.get('unionid')
        user.session_key = user_info.get('session_key'),
        user.jwt_revoked = False
    else:
        # 创建新用户
        user = User(
            wechat_openid=openid,
            wechat_unionid=user_info.get('unionid'),
            session_key=user_info.get('session_key')
        )
        db.session.add(user)

    try:
        # 提交更改到数据库
        db.session.commit()
        return user  # 返回用户对象，供后续使用
    except Exception as e:
        # 回滚事务以防止数据不一致
        db.session.rollback()
        raise e  # 抛出异常以便外部捕获并处理


def wechat_login(code):
    """处理小程序登录，生成并下发 JWT"""
    # 获取微信会话信息
    session_info = get_wechat_session_info(code)

    if 'errcode' in session_info:
        return jsonify({'error': session_info['errmsg']}), 400

    openid = session_info.get('openid')
    unionid = session_info.get('unionid')
    session_key = session_info.get('session_key')

    if not openid:
        return jsonify({'error': 'Failed to get OpenID'}), 400

    user_info = {
        'openid': openid,
        'unionid': unionid,
        'session_key': session_key
    }

    # 保存或更新用户信息
    user = save_user_info(user_info)

    # 生成 JWT 并返回给客户端
    token = generate_jwt(user)

    return jsonify({
        'message': 'Login successful',
        'token': token,  # 将 token 下发给客户端
        'openid': openid,
        'unionid': unionid
    }), 200


def get_all_users():
    """获取所有用户信息"""
    try:
        users = User.query.all()  # 获取所有用户记录
        user_list = [user.to_dict() for user in users]  # 将每个用户对象转换为字典
        return jsonify(user_list), 200
    except Exception as e:
        # 返回500错误和错误信息
        return jsonify({'error': str(e)}), 500


def get_user_info(openid):
    """根据 OpenID 获取用户信息"""
    try:
        user = User.query.filter_by(wechat_openid=openid).first()  # 根据 OpenID 查询用户
        if user:
            return jsonify(user.to_dict()), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        # 返回500错误和错误信息
        return jsonify({'error': str(e)}), 500


def get_user_self_info(current_user):
    """根据用户登录令牌 JWT 获取用户自身的信息"""
    try:
        user = User.query.filter_by(user_id=current_user.user_id).first()  # 根据 OpenID 查询用户
        if user:
            return jsonify(user.to_dict()), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        # 返回500错误和错误信息
        return jsonify({'error': str(e)}), 500


def generate_jwt(user):
    """生成 JWT"""
    print(user.user_id)
    token = jwt.encode({
        'user_id': user.user_id,
        'role': user.role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRATION_DELTA)  # 有效期限在config中设置
    }, SECRET_KEY, algorithm='HS256')
    print("Token: ", token)
    return token


def update_user_role(caller_role: str, user_id: str, new_role: str):
    # 如果调用者的角色是guest或者user，则没有调用权限，但这个由权限控制的修饰器（钩子）控制
    user = User.query.get(user_id)
    if not user:
        raise ValueError('User not found')

    # 确保新的角色有效
    if new_role not in ROLE_LEVEL:
        raise ValueError('Invalid role')

    caller_role_level = ROLE_LEVEL[caller_role]
    # print("调用者角色：", caller_role_level)
    user_role_level = ROLE_LEVEL[user.role]
    # print("用户角色：", user_role_level)
    new_role_level = ROLE_LEVEL[new_role]
    # print("新用户角色：", new_role_level)

    # 权限数字越小，权限越大!!

    # 确保调用者有权限更改角色
    if caller_role_level > user_role_level:
        raise ValueError('Caller does not have permission to modify this user\'s role')

    # 确保新角色不高于调用者的角色
    if new_role_level < caller_role_level:
        raise ValueError('New role is higher than caller\'s role')

    # 新角色不与原角色相同
    if new_role_level == user_role_level:
        raise ValueError('New role is the same as user\'s old role')

    # 更新用户角色并标记 JWT 为无效
    user.role = new_role
    user.jwt_revoked = True

    db.session.commit()


def bind_phone(user_id, phone_number, code):
    """
    绑定手机号，验证通过则进行绑定或换绑操作
    :param user_id: 用户ID
    :param phone_number: 要绑定的手机号
    :param code: 用户输入的验证码
    :return: 绑定结果
    """
    # 先验证短信验证码
    if not verify_sms_code(user_id, phone_number, code):
        return jsonify({'error': 'Invalid or expired verification code'}), 400

    # 查询用户是否存在
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在/非法用户。'}), 404

    if phone_number == user.phone_number:
        return jsonify({'error': "新旧手机号不能一致。"}), 500

    # 如果用户已有绑定的手机号，说明是换绑操作
    if user.phone_number:
        old_phone = user.phone_number
        user.phone_number = phone_number  # 换绑手机号
        action = f"Phone number changed from {old_phone} to {phone_number}"
    else:
        # 如果没有绑定的手机号，则是首次绑定
        user.phone_number = phone_number
        action = f"Phone number {phone_number} successfully bound"

    try:
        # 保存到数据库
        db.session.commit()
        return jsonify({'message': action}), 200
    except Exception as e:
        db.session.rollback()  # 出现异常时回滚数据库
        return jsonify({'error': str(e)}), 500
