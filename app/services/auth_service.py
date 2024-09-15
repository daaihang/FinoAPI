import datetime
import os

import jwt
import requests
import json
from flask import jsonify
from app.models import User
from app import db
from config.base import Config  # 导入配置类

# 从环境变量获取 AppID 和 AppSecret
WECHAT_APP_ID = os.getenv('WECHAT_APP_ID')
WECHAT_APP_SECRET = os.getenv('WECHAT_APP_SECRET')
SECRET_KEY = os.getenv('SECRET_KEY')

JWT_EXPIRATION_DELTA = Config.JWT_EXPIRATION_DELTA

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
        user.session_key = user_info.get('session_key')
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


def generate_jwt(user):
    """生成 JWT"""
    print(user.user_id)
    token = jwt.encode({
        'user_id': user.user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRATION_DELTA)  # 2小时有效
    }, SECRET_KEY, algorithm='HS256')
    print(token)
    return token