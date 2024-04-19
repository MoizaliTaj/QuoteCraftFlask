from flask import Flask
from application.config import LocalDevelopmentConfig
import os
from application.database import db


def create_app():
    app = Flask(__name__, template_folder="templates")
    if os.getenv('ENV', "development") == "production":
        raise Exception("Currently no production config is setup.")
    else:
        app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    app.app_context().push()
    return app


app = create_app()

from application.controllers import *

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=1986, debug=True)
