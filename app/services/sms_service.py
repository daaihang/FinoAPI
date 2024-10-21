import random
from datetime import datetime, timedelta
from app.models import SmsRecord
from app.services.external_service import send_sms
from config.base import Config
from app import db


# 发送验证码函数
def send_verification_code(user_id, phone_number):
    code = str(random.randint(100000, 999999))  # 生成6位数验证码
    valid_minutes = str(Config.SMS_VALIDITY_MINUTES)  # 从配置文件获取有效时间
    sms_type = 'verification'  # 短信类型设定为验证码

    try:
        # 使用已提供的 send_sms 函数
        template_id = "2172591"
        params = [code, valid_minutes]
        send_sms(phone_number, template_id, params)

        # 发送成功后，创建短信记录
        sms_record = SmsRecord(
            user_id=user_id,
            sms_type=sms_type,
            phone=phone_number,
            contact=code,
            status=True  # 成功发送
        )
        db.session.add(sms_record)
        db.session.commit()

        return {'success': True}
    except Exception as e:
        # 发送失败，记录错误
        sms_record = SmsRecord(
            user_id=user_id,
            sms_type=sms_type,
            phone=phone_number,
            contact=code,
            status=False  # 发送失败
        )
        db.session.add(sms_record)
        db.session.commit()

        return {'success': False, 'error': str(e)}


# 检查是否频繁发送
def validate_frequent_send(user_id, phone_number):
    one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
    ten_seconds_ago = datetime.utcnow() - timedelta(seconds=10)

    # 获取最近的发送记录
    last_sms = SmsRecord.query.filter_by(user_id=user_id).order_by(SmsRecord.created_at.desc()).first()

    if last_sms:
        # 同一用户同一手机号，1分钟内不能再次发送
        if last_sms.phone == phone_number and last_sms.created_at > one_minute_ago:
            return False
        # 同一用户不同手机号，10秒内不能再次发送
        if last_sms.phone != phone_number and last_sms.created_at > ten_seconds_ago:
            return False

    # 检查最近是否有频繁操作（5次以上发送）
    five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
    recent_sms_count = SmsRecord.query.filter(SmsRecord.user_id == user_id,
                                              SmsRecord.created_at > five_minutes_ago).count()
    if recent_sms_count >= 5:
        return False

    return True


# 验证验证码
def verify_sms_code(user_id, phone_number, code):
    valid_minutes = Config.SMS_VALIDITY_MINUTES
    valid_time_limit = datetime.utcnow() - timedelta(minutes=valid_minutes)

    # 获取最新的验证码记录
    sms_record = SmsRecord.query.filter_by(
        user_id=user_id, phone=phone_number, sms_type='verification', contact=code, status=True
    ).order_by(SmsRecord.created_at.desc()).first()

    if sms_record and sms_record.created_at > valid_time_limit:
        return True
    return False
