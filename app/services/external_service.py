import json
import os
import time
from io import BytesIO

from qcloud_cos import CosConfig, CosS3Client, CosServiceError
from tencentcloud.common import credential
from tencentcloud.common.exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.sms.v20210111 import sms_client, models

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