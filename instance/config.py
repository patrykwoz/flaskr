import os

SECRET_KEY='dev'
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_URL = 'postgresql:///flaskr'

# DATABASE = os.path.join(BASE_DIR, 'flaskr.sqlite')
# DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
# SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(app.instance_path, 'flaskr.sqlite'))