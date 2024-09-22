def register_routes(app):
    from app.api import auth, event, external

    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(event.bp, url_prefix='/api/event')
    app.register_blueprint(external.bp, url_prefix='/api/external')