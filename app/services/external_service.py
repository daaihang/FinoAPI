import json
import os
import time
from io import BytesIO

import requests
from qcloud_cos import CosConfig, CosS3Client, CosServiceError
from tencentcloud.common import credential
from tencentcloud.common.exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.sms.v20210111 import sms_client, models

from app import db
from app.models import SensitiveData
from config.base import Config

# 初始化腾讯云 COS 客户端
cos_config = CosConfig(
    Region=Config.COS_REGION,
    SecretId=Config.COS_SECRET_ID,
    SecretKey=Config.COS_SECRET_KEY
)
client = CosS3Client(cos_config)


# 获取目录路径
def get_directory(file_type):
    directories = {
        "avatar": Config.AVATAR_FOLDER,
        "details": Config.DETAILS_FOLDER,
        "poster": Config.POSTER_FOLDER,
        "announcement": Config.ANNOUNCEMENT_FOLDER,
        "attachment": Config.ATTACHMENT_FOLDER,
    }
    return directories.get(file_type, None)


def handle_file_upload(file_type, file, user_id):
    directory = get_directory(file_type)
    if directory is None:
        return {"error": "Invalid file type"}, 400

    # 头像时使用用户 ID 作为文件名，其他类型保留原文件名并加上时间戳
    if file_type == "avatar":
        file_name = f"{user_id}{os.path.splitext(file.filename)[-1]}"  # 保留文件扩展名
    else:
        file_name = f"{user_id}_{int(time.time())}_{file.filename}"

    object_key = f"{directory}/{file_name}"

    try:
        response = client.put_object(
            Bucket=Config.COS_BUCKET_NAME,
            Body=file,
            Key=object_key,
        )
        return {"message": "File uploaded successfully", "ETag": response['ETag'], "file_path": object_key}, 200
    except Exception as e:
        return {"error": str(e)}, 500


def get_file_from_cos(file_key):
    try:
        # 从COS获取文件对象
        response = client.get_object(
            Bucket=Config.COS_BUCKET_NAME,
            Key=file_key
        )

        # 获取文件内容
        file_stream = BytesIO(response['Body'].get_raw_stream().read())

        # 获取文件的MIME类型和文件名
        content_type = response['Content-Type']
        file_name = file_key.split('/')[-1]  # 获取文件名

        # 返回所有响应头和文件内容
        return file_stream, content_type, file_name, response

    except CosServiceError as e:
        raise CosServiceError(f"Error occurred when downloading file: {e}")


def send_sms(phone_number, template_id, params):
    """
    发送短信逻辑函数。

    :param phone_number: str 接收短信的手机号
    :param template_id: str 短信模板ID
    :param params: list 短信模板的参数, 例如 [验证码, 过期时间]
    :return: dict 发送结果
    """
    try:
        # 实例化一个认证对象，入参需要传入腾讯云账户 SecretId 和 SecretKey
        cred = credential.Credential(Config.SMS_SECRET_ID, Config.SMS_SECRET_KEY)

        # 实例化一个http选项
        httpProfile = HttpProfile()
        httpProfile.endpoint = "sms.tencentcloudapi.com"

        # 实例化一个client选项
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile

        # 实例化要请求产品的client对象
        client = sms_client.SmsClient(cred, "ap-guangzhou", clientProfile)

        # 实例化一个请求对象
        req = models.SendSmsRequest()

        # 填充请求参数
        req.SmsSdkAppId = Config.SMS_SDK_APP_ID
        req.SignName = Config.SMS_SMS_SIGN
        req.TemplateId = template_id
        req.PhoneNumberSet = [phone_number]  # 接收者手机号
        req.TemplateParamSet = params  # 短信模板参数

        # 发送短信
        resp = client.SendSms(req)

        # 返回的resp是一个SendSmsResponse的实例
        return json.loads(resp.to_json_string())

    except TencentCloudSDKException as err:
        return {"error": str(err)}


def refresh_access_token():
    url = "https://api.weixin.qq.com/cgi-bin/stable_token"
    payload = {
        "grant_type": "client_credential",
        "appid": Config.WECHAT_APP_ID,
        "secret": Config.WECHAT_APP_SECRET,
        "force_refresh": True
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

        access_token = data.get("access_token")

        if access_token:
            # 查找是否已存在
            existing_data = SensitiveData.query.filter_by(key_name='access_token').first()

            if existing_data:
                # 更新已存在的记录
                existing_data.key_value = access_token
                existing_data.expires_in = data.get("expires_in")
            else:
                # 新建记录
                existing_data = SensitiveData(key_name='access_token', key_value=access_token,
                                              expires_in=data.get("expires_in"))
                db.session.add(existing_data)

            db.session.commit()
            return {"success": True}
        else:
            return {"success": False, "error": data}  # 返回错误信息
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}  # 返回请求异常信息


def get_student_list(search: str) -> dict:
    """获取学生列表的逻辑函数"""
    api_url = 'https://gw.wozaixiaoyuan.com/addressBook/mobile/student/studentListForCon'
    headers = {
        'jwsession': 'fb7816fe23fd4d20abd41fc1855f2dc4',
        'Content-Type': 'application/json'
    }
    payload = {'condition': search}

    try:
        # 发送 POST 请求
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()  # 抛出异常以捕获错误
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching student list: {str(e)}")


