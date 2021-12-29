from os import path
from datetime import date
from enum import Enum
from flask import url_for

from goodplays import app, db


LOCAL_IMAGE_DIR = path.join(path.abspath(path.dirname(__file__)),
    'static', 'img')


class Status(Enum):
    default = 0
    interested = 1
    playing = 2
    played = 3
    completed = 4
    hundred = 5
    abandoned = 6

    @classmethod
    def in_use(cls):
        return [
            cls.interested, cls.playing, cls.played, cls.completed,
            cls.hundred, cls.abandoned
        ]

    @classmethod
    def filters(cls):
        return [cls.interested, cls.playing, cls.completed, cls.abandoned]

    @classmethod
    def choices(cls):
        return [(item, item.pretty()) for item in cls.in_use()]

    @classmethod
    def coerce(cls, item):
        return item if isinstance(item, cls) else \
            cls[item] if item is not None else None

    def pretty(self):
        return '100%' if self == Status.hundred else self.name.capitalize()

    @property
    def is_completed(self):
        return self in (Status.played, status.completed, status.hundred)

    def __str__(self):
        return str(self.name)


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
        return f'<User {self.id}>'


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
    company = db.Column(db.String)
    abbreviation = db.Column(db.String)
    released = db.Column(db.Date)
    gb_id = db.Column(db.Integer, unique=True)
    gb_url = db.Column(db.String)
    image_url = db.Column(db.String)
    games = db.relationship(
        'Game',
        back_populates='platforms',
        secondary=GamePlatform,
        lazy='dynamic'
    )

    def __repr__(self):
        return f'<Platform {self.name}>'


class Game(db.Model):
    __tablename__ = 'Game'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    released = db.Column(db.Date)
    added = db.Column(db.Date, default=date.today)
    gb_id = db.Column(db.Integer, unique=True)
    gb_url = db.Column(db.String)
    image_url = db.Column(db.String)
    image_file = db.Column(db.String)
    platforms = db.relationship(
        'Platform',
        back_populates='games',
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
    def year(self):
        return self.released.year if self.released else None

    @property
    def rating(self):
        if not self in db.session: return None
        plays = self.plays.filter(Play.rating > 0).all()
        return None if not plays else sum(p.rating for p in plays) / len(plays)

    @property
    def stars(self):
        return u'\u2605' * round(self.rating / 2) + \
            u'\u2606' * (5 - round(self.rating / 2)) if self.rating else ''

    @property
    def local_image_url(self):
        return url_for('static', filename=f'img/{self.image_file}') \
            if self.image_file else None

    @property
    def local_image_path(self):
        return path.join(LOCAL_IMAGE_DIR, self.image_file) \
            if self.image_file else None

    @property
    def current_image_is_local(self):
        return self.local_image_url == self.image_url

    def __repr__(self):
        year = f' ({self.year})' if self.year else ''
        return f'<Game {self.name}{year}>'


class Tag(db.Model):
    __tablename__ = 'Tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    plays = db.relationship(
        'Play',
        back_populates='tags',
        secondary=PlayTag,
        lazy='dynamic'
    )

    def __repr__(self):
        return f'<Tag {self.name}>'


class Play(db.Model):
    __tablename__ = 'Play'
    id = db.Column(db.Integer, primary_key=True)
    started = db.Column(db.Date)
    finished = db.Column(db.Date)
    rating = db.Column(db.Integer)
    status = db.Column(db.Enum(Status))
    comments = db.Column(db.String)
    fave = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
        server_default=db.false()
    )
    tags = db.relationship(
        'Tag',
        back_populates='plays',
        secondary=PlayTag,
        lazy='dynamic'
    )
    game_id = db.Column(db.Integer, db.ForeignKey('Game.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))

    @property
    def year(self):
        return self.finished.year if self.finished else None

    @property
    def completed(self):
        return self.status.is_completed

    @property
    def stars(self):
        return u'\u2605' * round(self.rating / 2) + \
            u'\u2606' * (5 - round(self.rating / 2)) if self.rating else ''

    def __repr__(self):
        return f'<Play {self.id}>'

