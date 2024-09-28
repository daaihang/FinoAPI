import os
import time
from qcloud_cos import CosConfig, CosS3Client
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
