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

questions = [
    "1": ["Which quote is from Dr. Shepherd?", "It is unnatural to have 0 dollars, 0 beers, or 0 goldfish crackers, and I agree with that.", "If you're playing a game, you're playing Quake.", "An internship with Microsoft, that would be pretty baller, right?"], #option 1
    "2": ["Which quote is from Dr. Shepherd?", "Remember, let bad things happen to a good person.", "Make sure you get it in there.", "Violence is fun, murder is wrong."], #option 3
    "3": ["Which quote is from Dr. Shepherd?", "They're selling holes!", "We're nuking all the children.", "He's cheery in the moring, but needs a cheeseburger by afternoon."], #option 2
    "4": ["Which quote is from Dr. Shepherd?", "I'm going to date all of you right now.", "Your body is a temple, stop eating markers", "To blob or not to blob? That's actually what Rene Descartes said. But it was french. le blob."], #option 3
    "5": ["Which quote is from Dr. Shepherd?", "Send me cash, you can use me however you want. Boy, that came out wrong.", "AM I NOT A SNACK FOR YOU ALL?", "I'm the Queen."], #option 1
    "6": ["Which quote is from Dr. Backman?", "Starts with 'ass,' ends in 'sets.' Assets.", "Ugh, you expect me to look at technology?", "I have broken it. I am a swine."], #option2
    "7": ["Which quote is from Dr. Backman?", "Have you broke the law since we've been in this room?", "Instead of slapping clothes off them, you could slap clothes on them. ", "Thats an evil way to position a chair. I hope you stub your toe."], #option1
    "8": ["Which quote is from Dr. Backman?", "I happen to know their flexible banana swords are quite robust.", "I'm a little masochistic these days.", "Remember, let bad things happen to good people."], #option3
    "9": ["Which quote is from Dr. Backman?", "AM I NOT A SNACK FOR YOU ALL?", "Did anyone have the phrase 'little potato balls' on their bingo cards?", "How do I put his skin back on?"], #option 1
    "10": ["Which quote is from Dr. Stone?", "LET ME COOK, LET ME COOK", "I'm the Queen", "You can bang a bool, but you can't negate it. "], #option 2
    "11": ["Which quote is from Dr. Stone?", "Who's fault is that? Russia? Freaking Russia... dicks.", "Me, the non-dock painter" ,"You gonna take that? Good boy."] #option 3
]

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