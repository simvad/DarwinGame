from flask import Blueprint, render_template, jsonify, request, Response, session, redirect, url_for
from app.models.game import game_manager
from app.models.database import Admin
import json
import time

game_bp = Blueprint('game', __name__)

@game_bp.route('/')
def home():
    if 'admin_id' in session:
        admin = Admin.query.get(session['admin_id'])
        if admin:
            return redirect(url_for('admin.admin'))
    return render_template('home.html')

@game_bp.route('/submit/<invite_code>')
def submit_page(invite_code):
    invite = game_manager.get_invite(invite_code)  # Need to add this method to GameManager
    if not invite or invite.used:
        return "Invalid or used invite code", 404
        
    game = game_manager.get_game(invite.game_id)
    if not game or game.started:
        return "Game not found or already started", 404
        
    return render_template('submit.html', 
                         invite_code=invite_code,
                         game_title=game.title)

@game_bp.route('/submit/<invite_code>', methods=['POST'])
def submit_bot(invite_code):
    try:
        if not request.is_json:
            return jsonify({
                'success': False, 
                'error_type': 'format',
                'errors': 'Invalid request format. Please submit the form properly.'
            }), 400

        data = request.get_json()
        
        if 'bot_name' not in data or 'bot_code' not in data:
            return jsonify({
                'success': False,
                'error_type': 'missing_fields',
                'errors': 'Missing required fields. Please provide both bot name and code.'
            }), 400

        success = game_manager.submit_bot(
            invite_code,
            data['bot_name'],
            data['bot_code']
        )
        return jsonify({'success': success})
    except ValueError as e:
        return jsonify({
            'success': False,
            'error_type': 'validation',
            'errors': str(e)
        })
    except Exception as e:
        print(f"Error submitting bot: {str(e)}")  # Log the error server-side
        return jsonify({
            'success': False,
            'error_type': 'unexpected',
            'errors': str(e)
        }), 500

@game_bp.route('/game/<game_id>')
def view_game(game_id):
    game = game_manager.get_game(game_id)
    if not game:
        return "Game not found", 404
    return render_template('game.html', game=game)

@game_bp.route('/game/status/<game_id>')
def game_status(game_id):
    def generate():
        game = game_manager.get_game(game_id)
        if not game:
            return
            
        last_round = -1
        while not game.started or last_round < game.current_round:
            if game.started and last_round < game.current_round:
                last_round = game.current_round
                data = {
                    'round': last_round,
                    'results': game.round_results[last_round]
                }
                yield f"data: {json.dumps(data)}\n\n"
            time.sleep(0.1)
            
    return Response(generate(), mimetype='text/event-stream')