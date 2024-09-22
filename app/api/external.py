"""
外部API，为了确保域名合法备案，将未备案的域名的API进行转发

Todo: 未来应该加上转发所有域名的操作，将常用API单独适配即可。
"""
import requests
from flask import Blueprint, request, jsonify

from app.services.decorators import jwt_required  # 导入装饰器

from config.base import Config

bp = Blueprint('external', __name__)


@bp.route('/photos/random', methods=['GET'])
def get_random_photo():
    # Unsplash API的URL
    unsplash_url = "https://api.unsplash.com/photos/random"

    # 获取请求中的所有查询参数
    params = request.args.to_dict()

    # 添加 Unsplash API 所需的访问密钥
    params['client_id'] = Config.UNSPLASH_SECRET_KEY

    try:
        # 通过requests模块发送请求给Unsplash API
        response = requests.get(unsplash_url, params=params)
        response.raise_for_status()  # 检查响应状态码是否为2xx

        # 将Unsplash的响应直接返回给客户端
        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:
        # 捕获请求错误并返回错误信息
        return jsonify({'error': str(e)}), 500