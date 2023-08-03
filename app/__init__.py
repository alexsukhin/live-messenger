from flask import Flask
import app.config

def create_app():
    app = Flask(__name__)
    app.config.from_object(app.config)

    return app