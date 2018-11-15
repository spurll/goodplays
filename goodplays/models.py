from datetime import date
from enum import Enum

from goodplays import app, db


class Status(Enum):
    default = 0
    interested = 1
    playing = 2
    completed = 3
    hundred_percent = 4
    abandoned = 5


class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, index=True, unique=True)
    email = db.Column(db.String, index=True)
    plays = db.relationship(
        'Play',
        backref='user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    games_added = db.relationship('Game', backref='added_by', lazy='dynamic')

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def is_admin(self):
        return self.id in app.config["ADMIN_USERS"]

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User {}>'.format(self.id)


# Configure many-to-many relationship without making a do-nothing class.
# https://stackoverflow.com/a/23424290
PlayTag = db.Table(
    'PlayTag',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('play_id', db.Integer, db.ForeignKey('Play.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('Tag.id'))
)


GamePlatform = db.Table(
    'GamePlatform',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('game_id', db.Integer, db.ForeignKey('Game.id')),
    db.Column('platform_id', db.Integer, db.ForeignKey('Platform.id'))
)


class Platform(db.Model):
    __tablename__ = 'Platform'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    games = db.relationship(
        'Game',
        backref='platform',
        secondary=GamePlatform,
        lazy='dynamic'
    )

    def __repr__(self):
        return '<Platform {}>'.format(self.name)


class Game(db.Model):
    __tablename__ = 'Game'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    year = db.Column(db.Integer)
    added = db.Column(db.Date, default=date.today)
    art_url = db.Column(db.String)
    gb_id = db.Column(db.String)
    gb_url = db.Column(db.String)
    platforms = db.relationship(
        'Platform',
        backref='game',
        secondary=GamePlatform,
        lazy='dynamic'
    )
    plays = db.relationship(
        'Play',
        backref='game',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    added_by_id = db.Column(db.String, db.ForeignKey('User.id'), nullable=True)

    @property
    def rating(self):
        plays = self.plays.all()
        return sum(p.rating for p in plays) / len(plays) if plays else None

    def __repr__(self):
        return '<Game {}{}>'.format(
            self.name, ' (' + self.year + ')' if self.year else ''
        )


class Tag(db.Model):
    __tablename__ = 'Tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    plays = db.relationship(
        'Play',
        backref='tag',
        secondary=PlayTag,
        lazy='dynamic'
    )

    def __repr__(self):
        return '<Tag {}>'.format(self.name)


class Play(db.Model):
    __tablename__ = 'Play'
    id = db.Column(db.Integer, primary_key=True)
    started = db.Column(db.Date)
    finished = db.Column(db.Date)
    rating = db.Column(db.Integer)
    status = db.Column(db.Enum(Status))
    comments = db.Column(db.String)
    tags = db.relationship(
        'Tag',
        backref='play',
        secondary=PlayTag,
        lazy='dynamic'
    )
    game_id = db.Column(db.Integer, db.ForeignKey('Game.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))

    def __repr__(self):
        return '<Play {}>'.format(self.name)
