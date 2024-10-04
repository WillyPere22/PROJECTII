from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from config import Config  # Ensure this imports your Config class correctly
import logging
from logging.handlers import RotatingFileHandler

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'main.login'  # Redirect to login page if not logged in
login_manager.login_message_category = 'info'  # Flash message category for login
mail = Mail()
migrate = Migrate()

def create_app(config_class=Config):
    """
    Flask application factory to create the app instance.
    :param config_class: The configuration class to use for the app.
    :return: The Flask app instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)  # Load config from the specified class

    # Initialize extensions with the app
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    # Set up logging
    setup_logging(app)

    # Import and register routes after initializing the app
    from app.routes import bp as main  # Import the Blueprint directly with an alias
    app.register_blueprint(main)  # Register the Blueprint

    # User loader function for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        """Load a user given the user ID."""
        from .models import User  # Import User here to avoid circular import
        return User.query.get(int(user_id))

    return app

def setup_logging(app):
    """Set up logging configuration."""
    # Create a directory for logs if it doesn't exist
    import os
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Set up a rotating file handler
    handler = RotatingFileHandler('logs/app.log', maxBytes=10000, backupCount=10)
    handler.setLevel(logging.INFO)

    # Create a logging format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the app's logger
    app.logger.addHandler(handler)

    # Log an entry when the application starts
    app.logger.info('Application startup')

# Automatically create the migration repository and apply initial migration if run directly
if __name__ == "__main__":
    app = create_app()  # Create the app instance
