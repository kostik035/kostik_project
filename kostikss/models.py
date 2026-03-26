from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='buyer')
    bio = db.Column(db.Text, default='')
    rating = db.Column(db.Float, default=0.0)
    completed_orders = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Gig(db.Model):
    __tablename__ = 'gigs'

    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    basic_price = db.Column(db.Float, nullable=False)
    basic_delivery = db.Column(db.Integer, nullable=False)
    basic_features = db.Column(db.Text, default='')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    seller = db.relationship('User', foreign_keys=[seller_id], backref='gigs')


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    gig_id = db.Column(db.Integer, db.ForeignKey('gigs.id'))
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    gig = db.relationship('Gig', backref='orders')
    buyer = db.relationship('User', foreign_keys=[buyer_id], backref='purchases')
    seller = db.relationship('User', foreign_keys=[seller_id], backref='sales')