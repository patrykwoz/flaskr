import os
from flask import Flask, render_template, jsonify
from celery_app import celery_init_app
from tasks import add_together
from urllib.parse import urlparse


def create_app(test_config=None) -> Flask:
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # Fetch the DATABASE_URL from the environment variable
    DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql:///flaskr')

    # Check if the URL needs to be modified for SQLAlchemy compatibility
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    url = urlparse.urlparse(os.environ.get('REDISCLOUD_URL'))
    r = redis.Redis(host=url.hostname, port=url.port, password=url.password)

    # Set SECRET_KEY and DATABASE URL from environment variables with fallback values
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'devnotcompletelyrandomsecretkey'),
        SQLALCHEMY_DATABASE_URI=DATABASE_URL,
        CELERY=dict(
            broker_url=os.environ.get('REDISCLOUD_URL', 'redis://localhost'),
            result_backend=os.environ.get('REDISCLOUD_URL', 'redis://localhost'),
            task_ignore_result=True,
            task_serializer='json',
            result_serializer='json',
            accept_content=['json'],
        ),
    )
    app.config.from_prefixed_env()

    
    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    celery_app = celery_init_app(app)

    # A simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from flask import request

    @app.get("/add")
    def render_add():
        
        return render_template('add.html')

    @app.post("/add")
    def start_add() -> dict[str, object]:
        a = request.form.get("a", type=int)
        b = request.form.get("b", type=int)
        result = add_together.delay(a, b)
        return {"result_id": result.id}
    
    @app.post("/add-redis")
    def start_add_redis() -> dict[str, object]:
        a = request.form.get("a", type=int)
        b = request.form.get("b", type=int)
        result = add_together.delay(a, b)
        
        # Store the result in Redis with a unique key
        result_key = f"result:{result.id}"
        app.config['REDIS_CONNECTION'].set(result_key, result.result)
        
        return {"result_id": result.id}

    from celery.result import AsyncResult

    @app.get("/result/<id>")
    def task_result(id: str):
        result = AsyncResult(id)
        response = {
            "ready": result.ready(),
            "successful": result.successful(),
            "value": result.result if result.ready() else None,
        }
        return jsonify(response)
    
    @app.get("/result-redis/<id>")
    def task_result_redis(id: str):
        result_key = f"result:{id}"  # Construct the result_key based on the 'id' parameter
        redis_connection = app.config.get('REDIS_CONNECTION')
        
        if redis_connection is None:
            return jsonify({"error": "Redis connection not available"}), 500
        
        result = redis_connection.get(result_key)
        
        if result is not None:
            response = {
                "ready": True,  # You may need to determine readiness based on your application logic
                "successful": True,  # You may need to determine success based on your application logic
                "value": result.decode()  # Assuming the result is a bytes-like object, convert it to a string
            }
        else:
            response = {
                "ready": False,
                "successful": False,
                "value": None
            }
        
        return jsonify(response)

    from .models import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app
