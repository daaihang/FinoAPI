def register_routes(app):
    from app.api import auth

    app.register_blueprint(auth.bp, url_prefix='/api/auth')
