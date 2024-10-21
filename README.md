![FinoLab-Logo.png](./static/FinoLab-Logo.png)

## FinoLab 小程序后端 - FinoAPI

> 开发中

使用Flask开发，纯后端无中后台。

## JWT 在请求头中的使用说明

遇到需要权限的API时，需要在Header中包含JWT Session Token，字段为`Authorization`，值为JWT Session Token。

## 启动说明

在启动flask前需连接数据库，创建数据模型，并提交至数据库。

`.env`文件创建于与`app.py`同级的目录下：

```text
# 开发环境，生产环境则设置为 'production'
FLASK_ENV=development

# 用于 Flask 的密钥
SECRET_KEY=******

# Debug 模式
DEBUG=True

# 微信小程序的 AppID
WECHAT_APP_ID=********

# 微信小程序的 AppSecret
WECHAT_APP_SECRET=********

# 数据库连接
SQLALCHEMY_DATABASE_URI=mysql://user:password@localhost:3306/finoapi
```

在根目录下使用命令：
```shell
flask db init  # 初始化数据模型
flask db migrate -m "commit"  # 提交数据模型
flask db upgrade  # 应用更改至数据库
```

运行 Flask 应用即可。

## 其他事项

`gunicorn.conf.py`文件为Docker中并发设计，在Windows下因为缺少库而测试暂时搁置。
具体 [看这里](https://zhuanlan.zhihu.com/p/78432719)。



现在还在开发阶段，在Docker中暂时使用python app.py启动程序。具体Docker包位于
[daaihang/finolab](https://hub.docker.com/repository/docker/daaihang/finolab/general)。根据未来规划，可能改变image的公开策略。



### 如何启动FinoAPI Docker Image

通过docker run命令：

```shell
docker run -d -p 8156:8156 \
  -e FLASK_ENV=production \
  -e SECRET_KEY=mysecretkey \
  -e DATABASE_URL=mysql://user:password@db:3306/mydb \
  your_docker_image
```

```shell
docker-compose --env-file .env up --build
```

### 获取当前操作的用户

可以通过修饰器`@jwt_required()`，在路由函数内直接获取当前用户的`user_id`。例如：

```python
from flask import Blueprint, g
from app.services.decorators import jwt_required
bp = Blueprint('auth', __name__)

@bp.route('/myinfo', methods=['GET'])
@jwt_required()
def get_self_user():
    """根据用户登录令牌 JWT 获取用户自身的信息"""
    print(g.current_user)
    return get_user_self_info(g.current_user)

def get_user_self_info():
    pass
```

`g.current_user`可以在路由函数获取`user_id`并传入逻辑函数内。