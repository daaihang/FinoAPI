from flask_admin.contrib.sqla import ModelView

class MyModelView(ModelView):
    # 去掉 is_accessible 方法，不进行权限检查
    pass
