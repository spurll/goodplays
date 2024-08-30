import os
import requests
from datetime import datetime, date
from howlongtobeatpy import HowLongToBeat

from goodplays import app, db
from goodplays.models import User, Game, Play, Platform, Tag, Status
from goodplays.gb import GiantBomb


HLTB = app.config.get('SHOW_HLTB')
GB = GiantBomb(app.config.get('GB_API_KEY'))
PAGE_SIZE = app.config.get('PAGE_SIZE', 20)
LOWER_TITLE = [
    'a', 'an', 'the', 'and', 'as', 'at', 'atop', 'but', 'by', 'for', 'from',
    'in', 'into', 'of', 'off', 'on', 'onto', 'out', 'over', 'per', 'to', 'up',
    'via', 'with'
]


def game(id):
    return Game.query.get(id)


def play(id):
    return Play.query.get(id)


def hltb(game):
    if not HLTB: return None

    if game.hltb_id:
        hltb_game = hltb_details(game.hltb_id)

        return hltb_game

    hltb_game = hltb_search(game.name)

    if hltb_game:
        game.hltb_id = hltb_game.game_id
        db.session.commit()

    return hltb_game


def hltb_search(name):
    results = HowLongToBeat().search(name)

    if results is not None and len(results) > 0:
        return max(results, key=lambda x: x.similarity)


def hltb_details(game_id):
    return HowLongToBeat().search_from_id(game_id)


def game_plays(user, game_id):
    if not user.is_authenticated:
        return None

    return user.plays \
        .filter_by(game_id=game_id) \
        .order_by(Play.started.desc(), Play.finished.desc()) \
        .all()


def platforms():
    return Platform.query.all()


def tags():
    return Tag.query.all()


def map_platforms(ids):
    return Platform.query.filter(Platform.id.in_(ids)).all()


def map_tags(names):
    return [
        Tag.query.filter_by(name=name.strip().lower()).one_or_none()
        or Tag(name=name.strip().lower())
        for name in names
        if name.strip().lower()
    ]


def existing_or_parse_game(gb):
    existing = Game.query.filter_by(gb_id=gb.get('id')).one_or_none()
    return (existing, True) if existing else (parse_gb_game(gb), False)


def existing_or_parse_platform(gb):
    existing = Platform.query.filter_by(gb_id=gb.get('id')).one_or_none()
    return existing if existing else parse_gb_platform(gb)


def parse_gb_game(gb):
    if not gb: return None

    # Produces incomplete "stub" platforms (e.g., company and release_date are
    # missing), but the alternative is extremely expensive, so just update the
    # stubs later. (Use gb.get(...) or {} because platforms returns None when
    # the game hasn't actually had a release.)
    platforms = map(existing_or_parse_platform, gb.get('platforms') or {})

    # This may be dangerous: what if a search result returns multiple games
    # with overlapping platforms? We may end up with multiple instances of each
    # platform (because it won't be in the DB yet) before any of them are
    # committed, then end up with integrity/nonunique errors on commit.
    # (Edit: Turns out that so long as it's all in one session, which it seems
    # to be, this works fine!)

    return Game(
        name=gb.get('name'),
        description=gb.get('deck'),
        released=release_date(gb),
        gb_id=gb.get('id'),
        gb_url=gb.get('site_detail_url'),
        image_url=gb.get('image', {}).get('small_url'),
        platforms=platforms
    )


def parse_gb_platform(gb):
    if not gb: return None

    # Handle company being set to None instead of {} (e.g., for pinball)
    gb['company'] = gb.get('company') or {}

    # Handle released being set to None (e.g., for pinball)
    released = datetime.strptime(gb['release_date'],
        '%Y-%m-%d %H:%M:%S').date() if gb.get('release_date') else None

    return Platform(
        name=gb.get('name'),
        abbreviation=gb.get('abbreviation'),
        company=gb['company'].get('name'),
        released=released,
        gb_id=gb.get('id'),
        gb_url=gb.get('site_detail_url'),
        image_url=gb.get('image', {}).get('small_url')
    )


def games(sort='added', page=1):
    if sort == 'added':
        sort = (Game.added.desc(), Game.id.desc())
    elif sort == 'released':
        sort = (Game.released.desc(),)
    elif sort == 'name':
        sort = (Game.name.asc(),)
    else:
        sort = None

    return Game.query \
        .order_by(*sort) \
        .limit(PAGE_SIZE) \
        .offset(PAGE_SIZE * (page - 1)) \
        .all()


def plays(user, fave=None, status=None, page=1):
    query = user.plays

    if fave:
        query = query.filter_by(fave=True) \
            .join(Play.game) \
            .order_by(Game.released.desc(), Game.name.asc())

    elif status in (Status.playing, Status.abandoned):
        query = query.filter_by(status=status).order_by(Play.started.desc())

    # Special case: Status.completed represents played, completed, and hundred
    elif status == Status.completed:
        query = query.filter(Play.status.in_(
            (Status.played, Status.completed, Status.hundred)
        )).order_by(Play.finished.desc())

    elif status is not None:
        query = query.filter_by(status=status) \
            .join(Play.game) \
            .order_by(Game.released.desc(), Game.name.asc())

    else:
        query = user.plays.order_by(Play.started.desc(), Play.finished.desc())

    return query.limit(PAGE_SIZE) \
        .offset(PAGE_SIZE * (page - 1)) \
        .all()


def search(query):
    results = Game.query \
        .filter_by(name=query.strip()) \
        .order_by(Game.released.desc()) \
        .all()

    fuzzy = Game.query \
        .filter(Game.name.like('%' + query.replace(' ', '%') + '%')) \
        .order_by(Game.name.asc()) \
        .all()

    for game in fuzzy:
        if len(results) >= PAGE_SIZE:
            break

        if game not in results:
            results.append(game)

    return results


def search_gb(query):
    results, error = GB.search(query, limit=PAGE_SIZE)

    if error:
        print(error)
    else:
        return list(map(existing_or_parse_game, results))


def platform_gb(gb_id):
    results, error = GB.platform(gb_id)

    if error:
        print(error)
    else:
        return existing_or_parse_platform(results)


def platforms_gb(query):
    """
    This returns too many results and needs pagination. Basically, don't try
    to add platforms to the database. Just import games from Giant Bomb and
    ensure that their platforms are added along with them instead.
    """
    results, error = GB.platforms()     # TODO: This returns too many results

    if error:
        print(error)
    else:
        return map(parse_gb_platform, results)


def add_game(user, game):
    """
    Adds an existing Game object (e.g., from Giant Bomb) to the database.
    """
    user.games_added.append(game)
    db.session.add(user)
    db.session.commit()
    return game


def add_gb(user, gb_id):
    """
    Searches Giant Bomb for the specified ID, creates a corresponding Game
    object, and adds it to the database.
    """
    game = Game.query.filter_by(gb_id=gb_id).one_or_none()

    if game:
        print(f'{game} already found. Nothing to do!')
        return game

    results, error = GB.game(gb_id)

    if error:
        print(error)
    else:
        game = existing_or_parse_game(results)[0]
        return add_game(user, game)


def new_game(user, **fields):
    """
    Creates a new Game object and adds it to the database.
    """
    game = Game(**fields)
    user.games_added.append(game)
    db.session.add(user)
    db.session.commit()
    return game


def new_play(user, **fields):
    """
    Creates a new Play object and adds it to the database.
    """
    play = Play(**fields)
    user.plays.append(play)
    db.session.add(user)
    db.session.commit()
    return play


def delete_play(play):
    db.session.delete(play)
    db.session.commit()


def delete_game(game):
    if not game.plays.count():
        db.session.delete(game)
        db.session.commit()


def edit_game(
    game, name, released, image_url, description, platforms, gb_id, hltb_id
):
    game.name = name
    game.released = released
    game.image_url = image_url
    game.description = description
    game.platforms = platforms
    game.gb_id = gb_id
    game.hltb_id = hltb_id
    db.session.commit()


def edit_play(play, started, finished, status, rating, comments, tags, fave):
    play.started = started
    play.finished = finished
    play.status = status
    play.rating = rating
    play.comments = comments
    play.tags = tags
    play.fave = fave
    db.session.commit()


def fave_play(play, fave):
    play.fave = fave
    db.session.commit()


def link_game(game, gb_id, update=False):
    """
    Link a game to the Giant Bomb database and update its data accordingly.
    """
    game.gb_id = gb_id

    if update:
        update_game(game)
    else:
        db.session.add(game)
        db.session.commit()


def link_platform(platform, gb_id, update=False):
    """
    Link a platform to the Giant Bomb database.
    """
    platform.gb_id = gb_id

    if update:
        update_game(platform)
    else:
        db.session.add(platform)
        db.session.commit()


def import_image(game):
    """
    Import a game's hotlinked cover image
    """
    if game.current_image_is_local:
        return

    # Set headers before making the request
    headers = {'User-Agent': 'goodplays'}
    response = requests.get(game.image_url, stream=True)

    if response.status_code != 200:
        print(f'Unable to import: server returned {response.status_code}')
        return

    # If there is an existing image, delete it
    if game.image_file and os.path.isfile(game.image_file):
        os.remove(game.local_image_path)

    _, ext = os.path.splitext(game.image_url)
    game.image_file = f'{game.id}{ext}'

    with open(game.local_image_path, 'wb') as handle:
        for block in response.iter_content(1024):
            handle.write(block)

    # Update game URL
    game.image_url = game.local_image_url

    db.session.commit()


def update_game(game):
    """
    Update a game by fetching its data from the Giant Bomb database.
    """
    gb, error = GB.game(game.gb_id)

    if error:
        print(error)
        return

    platforms = map(existing_or_parse_platform, gb.get('platforms') or {})

    game.name = gb.get('name') or game.name
    game.description = gb.get('deck') or game.description
    game.released = release_date(gb) or game.released
    game.gb_url = gb.get('site_detail_url') or game.gb_url
    game.image_url = gb.get('image', {}).get('small_url') or game.image_url
    game.platforms = platforms or game.platforms

    db.session.commit()

    return game


def release_date(gb):
    if gb.get('original_release_date'):
        return datetime.strptime(
            gb['original_release_date'], '%Y-%m-%d').date()

    return date(
        gb['expected_release_year'],
        gb['expected_release_month'],
        gb['expected_release_day']) if (
            gb.get('expected_release_day') and
            gb.get('expected_release_month') and
            gb.get('expected_release_year')) else None


def titlecase(str):
    """
    Capitalizes each word, except those in a proscribed list (e.g., articles,
    short prepositions, etc.). Note: all whitespace is replaced by single space
    characters.
    """
    return ' '.join(
        w.capitalize() if i == 0 or w not in LOWER_TITLE else w
        for i, w in enumerate(str.split())
    ) if str else str

