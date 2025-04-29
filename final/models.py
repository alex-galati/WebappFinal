# Set up the DB using the following commands:
# $ python
# > from app import db
# > db.create_all()
# > from models import User
# > admin = User(username='admin', email='admin@example.com')
# > db.session.add(admin)
# > db.session.commit()
# > User.query.all()

from app import db                                                        

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String(16), nullable=False)
    players = db.relationship('Player', backref='game', lazy=True)

    def serialize(self):
            return {
                'id': self.id,
                'game_id': self.game_id,
            }

    def __repr__(self):
        return f'<Game id={self.id}>'

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    game_id = db.Column(db.String(16), db.ForeignKey('game.game_id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'game_id': self.game.serialize(),
            'score': self.score
        }

    def __repr__(self):
        return f'<Player id={self.id}>'
