import os
from flask import Flask, render_template, jsonify
from celery_app import celery_init_app
from tasks import add_together

def create_app(test_config=None) -> Flask:
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # Fetch the DATABASE_URL from the environment variable
    DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql:///flaskr')

    # Check if the URL needs to be modified for SQLAlchemy compatibility
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    # Set SECRET_KEY and DATABASE URL from environment variables with fallback values
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'devnotcompletelyrandomsecretkey'),
        SQLALCHEMY_DATABASE_URI=DATABASE_URL,
        CELERY=dict(
            broker_url=os.environ.get('REDIS_URL', 'redis://localhost'),
            result_backend=os.environ.get('REDIS_URL', 'redis://localhost'),
            task_ignore_result=True,
            task_serializer='json',
            result_serializer='json',
            accept_content=['json'],
            broker_use_ssl={'ssl_cert_reqs': CERT_NONE}
        ),
    )
    app.config.from_prefixed_env()
    celery_app = celery_init_app(app)
    
    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)


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

    from .models import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app
