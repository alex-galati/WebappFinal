from flask import Flask, render_template, request, session, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room
import os 
import random, string

app = Flask(__name__)
app.secret_key = 'thereleasedateforhollowknight:silksong'

db_name = 'test.db'
sqlite_uri = f'sqlite:///{os.path.abspath(os.path.curdir)}/{db_name}'
app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

socketio = SocketIO(app)

from models import Game, Player

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('root.html')

@app.route('/join/<game_id>/', methods=['GET'])
def join(game_id):
    game = Game.query.filter_by(game_id=game_id).first()
    if not game:
        return render_template('root.html', message="Room does not exist.")
    return render_template('game.html', game_id=game_id) 

@app.route('/new/')
def new_game():
    length = 16
    game_id = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    while Game.query.filter_by(game_id=game_id).first() is not None: #As long as the game ID already exists, re-generate room code.
        game_id = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    new_game = Game(game_id=game_id)
    db.session.add(new_game)
    db.session.commit()
    
    return redirect(url_for('join', game_id=game_id))
    
@app.route('/add_player/', methods=['POST']) #New route meant to assist game.js with adding players to the database
def add_player():
    data = request.get_json()
    username = data.get('username')
    game_id = data.get('game_id')
    
    if not Game.query.filter_by(game_id=game_id).first():
        return jsonify({ 'error': 'Game not found.' }), 404
        
    new_player = Player(username=username, game_id=game_id)
    db.session.add(new_player)
    db.session.commit()
    
    return jsonify({'message': f'{username} added to the game {game_id}'}), 200
    
@socketio.on('player_joined') #three new socket routes meant to help broadcast the current members of the rooms to new people joining
def handle_player_joined(data): #player entering a username and "joining" the game
    username = data.get('username')
    game_id = data.get('game_id')
    emit('player_joined', {'username': username, 'game_id': game_id}, to=game_id)
    
@socketio.on('join_game') #joining a room on socket to track all users
def on_join(data): 
    game_id = data.get('game_id');
    if (game_id):
        join_room(game_id)
        print(f'User joined room: {game_id}')
    else: 
        print('No game ID provided in join_game event')

@app.route('/players/<game_id>') #getting all players currently in the room to display later. 
def get_players(game_id):
    game = Game.query.filter_by(game_id=game_id).first()
    if not game:
        return jsonify({'error': 'Game not found'}), 404

    players = Player.query.filter_by(game_id=game_id).all()
    return jsonify([player.username for player in players])
    
if __name__ == '__main__':
    socketio.run(app, debug=True)