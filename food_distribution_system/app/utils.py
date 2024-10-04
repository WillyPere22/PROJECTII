import os
import secrets
import cv2
import numpy as np
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer  # Updated import
from datetime import datetime
from app.models import User

# Password hashing utility
def hash_password(password):
    """
    Hash a password for storing.
    :param password: The plaintext password to hash.
    :return: The hashed password.
    """
    return generate_password_hash(password)

# Password verification utility
def verify_password(hashed_password, password):
    """
    Verify a stored password against a plaintext password.
    :param hashed_password: The hashed password.
    :param password: The plaintext password to compare.
    :return: True if the passwords match, False otherwise.
    """
    return check_password_hash(hashed_password, password)

# Token generation for account confirmation or password reset
def generate_token(user, expires_sec=1800):
    """
    Generate a token for confirming accounts or password reset.
    :param user: The user for whom to generate the token.
    :param expires_sec: Expiry time for the token in seconds (default is 1800s).
    :return: The generated token as a string.
    """
    s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
    return s.dumps({'user_id': user.id}).decode('utf-8')

# Verify a generated token
def verify_token(token):
    """
    Verify a token and retrieve the user.
    :param token: The token to verify.
    :return: The user if the token is valid, otherwise None.
    """
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        user_id = s.loads(token)['user_id']
    except:
        return None
    return User.query.get(user_id)

# Image resizing and saving utility for product images
def save_image(form_image, folder='static/product_images', size=(300, 300)):
    """
    Save an image after resizing it.
    :param form_image: The image to save.
    :param folder: The folder to save the image to (default is 'static/product_images').
    :param size: The size to resize the image to (default is (300, 300)).
    :return: The filename of the saved image.
    """
    # Create a random name for the image
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_image.filename)
    image_filename = random_hex + f_ext
    image_path = os.path.join(current_app.root_path, folder, image_filename)
    
    # Read and resize the image using OpenCV
    file_storage = form_image.stream
    img = cv2.imdecode(np.frombuffer(file_storage.read(), np.uint8), cv2.IMREAD_COLOR)
    
    # Resize the image
    img_resized = cv2.resize(img, size, interpolation=cv2.INTER_AREA)
    
    # Save the image
    cv2.imwrite(image_path, img_resized)
    
    return image_filename

# Utility to generate a unique order ID
def generate_order_id():
    """
    Generate a unique order ID based on the current timestamp.
    :return: The generated order ID.
    """
    return 'ORD' + datetime.now().strftime('%Y%m%d%H%M%S') + secrets.token_hex(4)

# Check user role utility
def is_vendor(user):
    """
    Check if the user is a vendor.
    :param user: The user to check.
    :return: True if the user is a vendor, False otherwise.
    """
    return user.role == 'vendor'

def is_farmer(user):
    """
    Check if the user is a farmer.
    :param user: The user to check.
    :return: True if the user is a farmer, False otherwise.
    """
    return user.role == 'farmer'
