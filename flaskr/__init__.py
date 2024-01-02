import os
from flask import Flask, render_template, jsonify
from celery_app import celery_init_app
from urllib.parse import urlparse
import redis
from celery.result import AsyncResult
from flask import request
from .models import db
from . import auth
from . import blog
from . import views

def create_app(test_config=None) -> Flask:
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # Fetch the DATABASE_URL from the environment variable
    DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql:///flaskr')

    # Check if the URL needs to be modified for SQLAlchemy compatibility
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    url = urlparse(os.environ.get('REDISCLOUD_URL', 'redis://localhost'))
    r = redis.Redis(host=url.hostname, port=url.port, password=url.password)

    # Set SECRET_KEY and DATABASE URL from environment variables with fallback values
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'devnotcompletelyrandomsecretkey'),
        SQLALCHEMY_DATABASE_URI=DATABASE_URL,
        CELERY=dict(
            broker_url=os.environ.get('REDISCLOUD_URL', 'redis://localhost'),
            result_backend=os.environ.get('REDISCLOUD_URL', 'redis://localhost'),
            task_ignore_result=True,
        ),
    )
    app.config.from_prefixed_env()
    celery_app = celery_init_app(app)

    # A simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'







    



    db.init_app(app)

    app.register_blueprint(views.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)

    app.add_url_rule('/', endpoint='index')

    return app
