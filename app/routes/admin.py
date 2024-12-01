from flask import Blueprint, render_template, session, jsonify, request, redirect, url_for
from app.models.game import game_manager
from app.models.database import Admin, db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    admin = Admin.query.filter_by(username=username).first()
    if admin and admin.check_password(password):
        session['admin_id'] = admin.id
        return jsonify({'success': True})
    
    return jsonify({
        'success': False, 
        'error': 'Invalid username or password'
    }), 401

@admin_bp.route('/admin')
def admin():
    if 'admin_id' not in session:
        return redirect(url_for('game_bp.home'))
    
    admin = Admin.query.get(session['admin_id'])
    if not admin:
        session.pop('admin_id', None)
        return redirect(url_for('game_bp.home'))
        
    return render_template('admin.html', games=game_manager.games)

@admin_bp.route('/admin/logout')
def logout():
    session.pop('admin_id', None)
    return redirect(url_for('game_bp.home'))

@admin_bp.route('/admin/create_game', methods=['POST'])
def create_game():
    if 'admin_id' not in session:
        return jsonify({'success': False}), 403
        
    data = request.json
    game_id = game_manager.create_game(
        title=data['title'],
        min_rounds=data['min_rounds'],
        max_rounds=data['max_rounds'],
        min_turns=data['min_turns'],
        max_turns=data['max_turns'],
        admin_id=session['admin_id']  # Pass admin_id to track who created the game
    )
    return jsonify({'game_id': game_id})

@admin_bp.route('/admin/create_invite/<game_id>', methods=['POST'])
def create_invite(game_id):
    if 'admin_id' not in session:
        return jsonify({'success': False}), 403
        
    try:
        invite_code = game_manager.create_invite(game_id)
        return jsonify({'invite_code': invite_code})
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@admin_bp.route('/admin/start_game/<game_id>', methods=['POST'])
def start_game(game_id):
    if 'admin_id' not in session:
        return jsonify({'success': False}), 403
        
    success = game_manager.start_game(game_id)
    return jsonify({'success': success})