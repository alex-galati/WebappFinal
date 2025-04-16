from flask import Flask, render_template, request, session, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
import os 
import random, string

app = Flask(__name__)
app.secret_key = ''

db_name = 'test.db'
sqlite_uri = f'sqlite:///{os.path.abspath(os.path.curdir)}/{db_name}'
app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import User

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('root.html')

@app.route('/join/<game_id>/', methods=['GET'])
def join(game_id):
    return render_template('game.html') 

@app.route('/new/')
def new_game():
    length = 16
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return redirect(url_for('join', game_id=random_string)) 
