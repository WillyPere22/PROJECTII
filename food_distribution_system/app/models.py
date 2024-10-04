from . import db
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin


# User roles: either a Farmer or a Vendor
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # Either 'farmer' or 'vendor'
    county = db.Column(db.String(50), nullable=False)  # Added county field
    sub_county = db.Column(db.String(50), nullable=False)  # Added sub-county field
    town = db.Column(db.String(50), nullable=False)  # Added town field
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    farmer_profile = db.relationship('Farmer', backref='user', uselist=False, lazy=True)
    vendor_profile = db.relationship('Vendor', backref='user', uselist=False, lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

    # Method to determine if user is active
    def is_active(self):
        return True  # Customize logic here if needed

    # Method to get the user's unique identifier
    def get_id(self):
        return self.id  # This is needed for Flask-Login

    # Method to check if the user is authenticated
    def is_authenticated(self):
        return True

    # Method to check if the user is anonymous
    def is_anonymous(self):
        return False

# Farmer model
class Farmer(db.Model):
    __tablename__ = 'farmers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    farm_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    products = db.relationship('Product', backref='farmer', lazy=True)

    def __repr__(self):
        return f'<Farmer {self.farm_name}>'


# Vendor model
class Vendor(db.Model):
    __tablename__ = 'vendors'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    shipping_address = db.Column(db.String(200), nullable=False)
    orders = db.relationship('Order', backref='vendor', lazy=True)

    def __repr__(self):
        return f'<Vendor {self.full_name}>'


# Product model
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    quantity_available = db.Column(db.Integer, nullable=False, default=0)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('OrderItem', backref='product', lazy=True)

    def __repr__(self):
        return f'<Product {self.name}>'


# Order model
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')  # Order status: Pending, Shipped, Delivered
    total_price = db.Column(db.Float, nullable=False)
    date_ordered = db.Column(db.DateTime, default=datetime.utcnow)
    order_items = db.relationship('OrderItem', backref='order', lazy=True)

    def __repr__(self):
        return f'<Order {self.id}, Status: {self.status}>'


# OrderItem model to represent the individual items in an order
class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<OrderItem {self.product.name} x {self.quantity}>'


# Feedback model for farmer-vendor interactions
class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # Rating out of 5
    comment = db.Column(db.Text, nullable=True)
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Feedback from Vendor {self.vendor_id} to Farmer {self.farmer_id}>'


# Create all tables in the database
def create_tables(app):
    with app.app_context():
        db.create_all()  # Create all tables
