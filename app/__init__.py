from flask import Flask
from .models.database import db, Admin
from .models.game import init_game_manager
import os

def create_app(config_name='production'):
    app = Flask(__name__)
    
    # Database configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    # Configure app based on environment
    if config_name == 'test':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        app.config['TESTING'] = True
    else:  # production
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'darwin_game.db')
        
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev'  # Change in production!
    
    # Initialize database
    db.init_app(app)
    
    # Create database tables and initialize test data if in test mode
    with app.app_context():
        db.drop_all()  # Reset database
        db.create_all()
        
        # Initialize game manager
        init_game_manager()
        
        if config_name == 'test':
            # Create test admin
            test_admin = Admin(username='test_admin')
            test_admin.set_password('test123')
            db.session.add(test_admin)
            db.session.commit()
            
            # Import game_manager after initialization
            from .models.game import game_manager
            
            # Create test game
            game_id = game_manager.create_game(
                title="Test Game",
                min_rounds=100,
                max_rounds=100,
                min_turns=100,
                max_turns=100,
                admin_id=test_admin.id
            )
            
            # Load and submit test bots
            from .test_bots import load_test_bots
            test_bots = load_test_bots()
            
            # Submit all test bots
            for bot_name, bot_code in test_bots.items():
                invite_code = game_manager.create_invite(game_id)
                game_manager.submit_bot(invite_code, bot_name, bot_code)
                
    # Register blueprints
    from .routes.admin import admin_bp
    from .routes.game import game_bp
    
    app.register_blueprint(admin_bp)
    app.register_blueprint(game_bp)
    
    return app
