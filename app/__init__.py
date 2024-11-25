from flask import Flask, render_template, redirect, url_for
from app.booking import bp as booking_bp


def create_app():
    app = Flask(__name__)

    app.register_blueprint(booking_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app
