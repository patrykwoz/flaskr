"""SQLAlchemy models for Idealog."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<User #{self.id}: {self.username}>"

    @classmethod
    def signup(cls, username, password):
        """Sign up user.

        Hashes password and adds user to system.
        """
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd,
        )

        db.session.add(user)
        return user
    
    @classmethod
    def hash_existing(cls, password):
        """Hash password for an existing user"""
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
        return hashed_pwd

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """
        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

class Post(db.Model):
    """User's post model."""

    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    created = db.Column(db.DateTime, nullable=False, default = datetime.utcnow)
    title = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)


    def __repr__(self):
        return f"<Post #{self.id}: {self.name}>"

    @classmethod
    def sorted_query(cls):
        return cls.query.order_by(cls.name).all()

class KnowledgeBase(db.Model):
    """User's knowledge base model."""

    __tablename__ = 'knowledge_bases'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    created = db.Column(db.DateTime, nullable=False, default = datetime.utcnow)
    title = db.Column(db.Text, nullable=False)
    json_object = db.Column(db.JSON)

    def __repr__(self):
        return f"<Knowledge Base #{self.id}: {self.name}>"