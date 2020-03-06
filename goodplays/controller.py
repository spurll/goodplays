from datetime import datetime, date

from goodplays import app, db
from goodplays.models import User, Game, Play, Platform, Tag, Status
from goodplays.gb import GiantBomb


GB = GiantBomb(app.config.get('GB_API_KEY'))
PAGE_SIZE = app.config.get('PAGE_SIZE', 20)


def game(id):
    return Game.query.get(id)


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


def plays(user, status=None, page=1):
    query = user.plays

    if status == Status.interested:
        query = query.filter_by(status=status) \
            .join(Play.game) \
            .order_by(Game.name.asc())

    elif status in (Status.playing, Status.abandoned):
        query = query.filter_by(status=status).order_by(Play.started.desc())

    elif status in (Status.completed, Status.hundred):
        query = query.filter_by(status=status).order_by(Play.finished.desc())

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


def edit_game(game, name, released, image_url, description, platforms):
    game.name = name
    game.released = released
    game.image_url = image_url
    game.description = description
    game.platforms = platforms
    db.session.commit()


def edit_play(play, started, finished, status, rating, comments, tags):
    play.started = started
    play.finished = finished
    play.status = status
    play.rating = rating
    play.comments = comments
    play.tags = tags
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

