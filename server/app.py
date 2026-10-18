import os

from flask import Flask, jsonify
from flask_migrate import Migrate
from marshmallow import ValidationError

from models import db
from routes import api

migrate = Migrate()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URI", "sqlite:///app.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Register routes blueprint
    app.register_blueprint(api)

    # Register error handlers
    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        return jsonify({"errors": err.messages}), 422

    @app.errorhandler(404)
    def handle_not_found(err):
        return jsonify({"error": "Resource not found."}), 404

    @app.errorhandler(400)
    def handle_bad_request(err):
        return jsonify({"error": "Bad request."}), 400

    return app


app = create_app()

if __name__ == "__main__":
    app.run(port=5555, debug=True)
