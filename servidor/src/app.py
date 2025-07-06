from flask import Flask
from flask_cors import CORS
from .routes import webtalk

def create_app():
    app = Flask(__name__)
    CORS(app)  # ← Isso libera CORS pro front
    app.register_blueprint(webtalk, url_prefix="/webtalk")
    return app