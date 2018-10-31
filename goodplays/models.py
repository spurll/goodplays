from datetime import date

from goodplays import app, db


class User(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, index=True, unique=True)
    email = db.Column(db.String, index=True)
    plays = db.relationship(
        'Play',
        backref='user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

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
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    games = db.relationship(
        'Game',
        backref='platform',
        secondary=GamePlatform,
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return '<Platform {}>'.format(self.name)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    year = db.Column(db.Integer)
    added = db.Column(db.Date, default=date.today)
    gb_uri = db.Column(db.String)       # TODO
    art_uri = db.Column(db.String)      # TODO: Allow users to upload if blank
    platforms = db.relationship(        # Dropdown? Should this go in Play?
        'Platform',
        backref='game',
        secondary=GamePlatform,
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    plays = db.relationship(
        'Play',
        backref='game',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return '<Tag {}{}>'.format(
            self.name, ' (' + self.year + ')' if self.year else ''
        )


# TODO: Seems like there's circular table dependency issue or something.
# Try to resolve it. If you can't, get rid of the secondaries and create some
# intermediate link table classes manually.


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    plays = db.relationship(
        'Play',
        backref='tag',
        secondary=PlayTag,
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return '<Tag {}>'.format(self.name)


class Play(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    started = db.Column(db.Date)
    finished = db.Column(db.Date)
    rating = db.Column(db.Integer)
    comments = db.Column(db.String)
    tags = db.relationship(
        'Tag',
        backref='play',
        secondary=PlayTag,
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Play {}>'.format(self.name)

