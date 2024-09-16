![FinoLab-Logo.png](./static/FinoLab-Logo.png)

## FinoLab 小程序后端 - FinoAPI

> 开发中

使用Flask开发，纯后端无中后台。

## JWT 在请求头中的使用说明

遇到需要权限的API时，需要在Header中包含JWT Session Token，字段为`Authorization`，值为JWT Session Token。

## 启动说明

在启动flask前需连接数据库，创建数据库模型。

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