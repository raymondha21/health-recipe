"""SQLAlchemy models for Health Recipe"""


from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )
    
    first_name = db.Column(
        db.Text,
        nullable=False,)

    last_name = db.Column(
        db.Text,
        nullable=False,)

    image_url = db.Column(
        db.Text,
        nullable=True,
        default="/static/images/default-pic.png",
    )

    height = db.Column(
        db.Float, 
        nullable=True,
    )

    weight = db.Column(
        db.Float, 
        nullable=True,
    )

    age = db.Column(
        db.Integer, 
        nullable=True,
    )

    gender = db.Column(
        db.Text, 
        nullable=True,
    )

    activity = db.Column(
        db.Float,
        nullable=True
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.username}>"

    @classmethod
    def signup(cls, username, password, first_name, last_name, image_url):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd,
            first_name=first_name,
            last_name=last_name,
            image_url=image_url,
        )

        db.session.add(user)
        return user

    likes = db.relationship('Recipe')

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

class Recipe(db.Model):
    """Model for user to associate favorite recipes"""

    __tablename__ = 'recipes'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    recipe_id = db.Column(
        db.Integer
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        nullable=False,
    )

    user = db.relationship('User')

    
def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)
