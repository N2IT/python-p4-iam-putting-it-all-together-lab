from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.schema import CheckConstraint
from sqlalchemy.orm import validates


from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)
    
    @hybrid_property
    def password_hash(self):
        raise AttributeError('not allowed to view password hash')

    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8')
        )
    
    recipes = db.relationship('Recipe', back_populates='user')

    def __repr__(self):
        return f'User {self.username}, ID {self.id}'

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    __table_args__ = (
        db.CheckConstraint('length(instructions) > 50', name = 'ck_instructions_length'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String(50), nullable=False)
    minutes_to_complete = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='recipes')

    # @validates('instructions')
    # def instructions(self, key, instructions):
    #     if len(instructions) < 50:
    #         raise ValueError('Instructions must have 50 characters minimum')
    #     return instructions

    # @hybrid_property
    # def instructions(self):
    #     return self._instructions

    # @instructions.setter
    # def instructions(self, value):
    #     if len(value) < 50:
    #         raise IntegrityError("Instructions must be at least 50 characters long.", value, None)
        
    #     self._instructions = value