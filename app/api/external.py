"""
外部API，为了确保域名合法备案，将未备案的域名的API进行转发

Todo: 未来应该加上转发所有域名的操作，将常用API单独适配即可。
"""
import time

import requests
from flask import Blueprint, request, jsonify, g, send_file, make_response
from qcloud_cos import CosServiceError

from app.services.decorators import jwt_required  # 导入装饰器
from app.services.external_service import handle_file_upload, send_sms, get_file_from_cos

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


@bp.route('/upload/<file_type>', methods=['POST'])
@jwt_required()
def upload_file(file_type):
    """上传文件到腾讯云 COS 到指定的目录"""
    file = request.files['file']  # 获取上传的文件
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    user_id = g.current_user.user_id  # 从 g 对象中获取用户 ID
    print(user_id)
    response, status_code = handle_file_upload(file_type, file, user_id)
    return jsonify(response), status_code


@bp.route('/file/<path:file_key>', methods=['GET'])
# @jwt_required()
# todo: 因为部分资源不方便带参数，暂时不用验证。需要未来强化逻辑函数权限认证。
def download_file(file_key):
    """
    从腾讯云 COS 下载文件并返回，同时返回文件的元数据信息
    :param file_key: COS 中文件的键 (文件路径)
    :return: 文件流和元数据信息
    """
    if not file_key:
        return jsonify({'error': 'file_key is required'}), 400

    try:
        # 调用函数获取 COS 文件及其所有响应信息
        file_stream, content_type, file_name, response_headers = get_file_from_cos(file_key)

        # 通过 Flask 的 send_file 返回文件，并设置相关参数
        response = make_response(send_file(
            file_stream,
            mimetype=content_type,  # COS 返回的 Content-Type
            download_name=file_name,  # 浏览器下载时显示的文件名
        ))

        # 添加所有响应头
        for header, value in response_headers.items():
            response.headers[header] = value

        return response

    except CosServiceError as e:
        return jsonify({'error': f'File download failed: {e}'}), 500



@bp.route('/send_sms', methods=['POST'])
@jwt_required()
def api_send_sms():
    data = request.json
    phone_number = data.get("phone_number")
    template_id = data.get("template_id")
    params = data.get("params")

    if not phone_number or not template_id:
        return jsonify({"error": "Phone number and template ID are required."}), 400

    result = send_sms(phone_number, template_id, params)
    return jsonify(result)
