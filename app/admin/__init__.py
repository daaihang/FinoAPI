from flask_admin import Admin
from .views import MyModelView  # 导入自定义视图
from app import db

admin = Admin(name='FinoLab 管理中岛', template_mode='bootstrap4')

def init_admin(app):
    admin.init_app(app)

    # 添加自定义的模型视图到管理页面
    from app.models import User, Event, SmsRecord
    admin.add_view(MyModelView(User, db.session))
    admin.add_view(MyModelView(Event, db.session))
    admin.add_view(MyModelView(SmsRecord, db.session))
