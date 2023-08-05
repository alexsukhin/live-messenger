from flask import Flask
from . import config

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app