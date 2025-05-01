from flask import Flask, render_template, request, session, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room
import os 
import random, string
'''
Current done:
 - Changed room code to all letters & uppercase
 - Removed placeholder players
 - Added scores to each player. *NOT ADDED SCORE TO HTML, JUST TO SCHEMA*
  - Make questions - SHEPHERD QUOTES
Need to do:
 - add score to HTML
'''

app = Flask(__name__)
app.secret_key = 'thereleasedateforhollowknight:silksong'

db_name = 'test.db'
sqlite_uri = f'sqlite:///{os.path.abspath(os.path.curdir)}/{db_name}'
app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

socketio = SocketIO(app)

active_answers = {}

questions = { #key: question, correct answer
    "1": ["Who said this quote: It is unnatural to have 0 dollars, 0 beers, or 0 Goldfish crackers, and I agree with that.", "Dr. Shepherd"], 
    "2": ["Who said this quote: Ugh, you expect me to look at technology?", "Dr. Backman"],
    "3": ["Who said this quote: Violence is fun, murder is wrong", "Dr. Shepherd"], 
    "4": ["Who said this quote: You gonna take that? Good boy.", "Dr. Stone"],
    "5": ["Who said this quote: We're nuking all of the children", "Dr. Shepherd"], 
    "6": ["Who said this quote: Have you broke the law since we've been in this room?", "Dr. Backman"],
    "7": ["Who said this quote: To blob or not to blob? That's actually what Rene Descartes said. But it was french. le blob.", "Dr. Shepherd"], 
    "8": ["Who said this quote: AM I NOT A SNACK FOR YOU ALL?", "Dr. Backman"],
    "9": ["Who said this quote: Send me cash, you can use me however you want. Boy, that came out wrong.", "Dr. Shepherd"],
    "10": ["Who said this quote: I'm the Queen.", "Dr. Stone"],
    "11": ["Who said this quote: Remember, let bad things happen to good people.", "Dr. Backman"], 
}

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
    return render_template('game.html', game_id=game_id, questions=questions) 

@app.route('/new/') 
def new_game():
    length = 16
    game_id = ''.join(random.choices(string.ascii_letters, k=length))
    
    while Game.query.filter_by(game_id=game_id).first() is not None: #As long as the game ID already exists, re-generate room code.
        game_id = ''.join(random.choices(string.ascii_letters, k=length))
    
    game_id = game_id.upper()
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
        
    new_player = Player(username=username, game_id=game_id, score=0)
    db.session.add(new_player)
    db.session.commit()
    
    return jsonify({'message': f'{username} added to the game {game_id}'}), 200
    
@socketio.on('player_joined') #three new socket routes meant to help broadcast the current members of the rooms to new people joining
def handle_player_joined(data): #player entering a username and "joining" the game
    username = data.get('username')
    game_id = data.get('game_id')
    emit('player_joined', {'username': username, 'game_id': game_id, 'score': 0}, to=game_id)
    
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
    return jsonify([{'username': player.username, 'score': player.score} for player in players])
    
@socketio.on('submit_answer')
def handle_submit_answer(data):
	game_id = data.get('game_id')
	username = data.get('username')
	question_number = str(data.get('question_number'))
	answer = data.get('answer')

	if not all([game_id, username, question_number, answer]):
		print("Incomplete answer submission:", data)
		return

	if game_id not in active_answers:
		active_answers[game_id] = {}
	if question_number not in active_answers[game_id]:
		active_answers[game_id][question_number] = {}

	active_answers[game_id][question_number][username] = answer

	expected_count = Player.query.filter_by(game_id=game_id).count()
	current_count = len(active_answers[game_id][question_number])

	print(f"[{game_id}] Q{question_number}: {current_count}/{expected_count} players answered.")

	if current_count == expected_count:
		correct_answer = questions[question_number][1]
		emit('all_answers_received', {
			'question_number': question_number,
			'correct_answer': correct_answer,
			'answers': active_answers[game_id][question_number]
		}, to=game_id)

@socketio.on('start_game')
def handle_start_game(data):
	game_id = data.get('game_id')
	if game_id:
		print(f"Starting game for room: {game_id}")
		emit('start_game', {}, to=game_id)

if __name__ == '__main__':
    socketio.run(app, debug=True)
