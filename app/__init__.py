from flask import Flask
from .models.database import db
import os

def create_app():
    app = Flask(__name__)
    
    # Database configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'darwin_game.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev'  # Change in production!
    
    # Initialize database
    db.init_app(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    from .routes.admin import admin_bp
    from .routes.game import game_bp
    
    app.register_blueprint(admin_bp)
    app.register_blueprint(game_bp)
    
    return app