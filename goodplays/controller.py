from datetime import datetime

from goodplays import app, db
from goodplays.models import User, Game, Play, Platform, Tag
from goodplays.gb import GiantBomb


PAGE_SIZE = app.config.get('PAGE_SIZE', 20)

GB = GiantBomb(app.config.get('GB_API_KEY'))


def games():
    return Games.all()


def plays(user):
    return user.plays.all()


def platforms():
    return Platforms.all()


def existing_or_parse_game(gb):
    existing = Game.query.filter_by(gb_id=gb.get('id')).one_or_none()
    return existing if existing else parse_gb_game(gb)


def existing_or_parse_platform(gb):
    existing = Platform.query.filter_by(gb_id=gb.get('id')).one_or_none()
    return existing if existing else parse_gb_platform(gb)


def parse_gb_game(gb):
    if not gb: return None

    """
    platforms = []

    for platform in gb.get('platforms', {}):
        existing = Platform.query.filter_by(
            gb_id=platform.get('id')
        ).one_or_none()

        if existing:
            platforms.append(existing)
        else:
            # TODO: This is very, very slow for games with many releases (e.g.,
            # Super Mario Bros.) Maybe use stubs?
            result = platform_gb(platform.get('id'))

            if result:
                platforms.append(result)
    """

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

    # TODO: I suspect that GB's /search endpoint isn't returning release date
    # info (usually, anyway); maybe querying for an individual /game will?
    released = gb.get('original_release_date')

    return Game(
        name=gb.get('name'),
        description=gb.get('deck'),
        released=(datetime.strptime(released, '%Y-%m-%d %H:%M:%S').date()
            if released else None),
        gb_id=gb.get('id'),
        gb_url=gb.get('site_detail_url'),
        image_url=gb.get('image', {}).get('small_url'),
        platforms=platforms
    )


def parse_gb_platform(gb):
    if not gb: return None

    if not gb.get('company'):
        # Handle company being set to None instead of {} (e.g., for pinball)
        gb['company'] = {}

    # Handle released being set to None (e.g., for pinball)
    dt = datetime.strptime(gb['release_date'], '%Y-%m-%d %H:%M:%S').date() \
        if gb.get('release_date') else None

    return Platform(
        name=gb.get('name'),
        abbreviation=gb.get('abbreviation'),
        company=gb['company'].get('name'),
        released=dt,
        gb_id=gb.get('id'),
        gb_url=gb.get('site_detail_url'),
        image_url=gb.get('image', {}).get('small_url')
    )


def games(page=1, order='added'):
    if order == 'added':
        order = Game.added.desc()
    elif order == 'name':
        order = Game.name.asc()
    elif order == 'year':
        order = Game.released.desc()
    else:
        order = None

    return (
        Game.query
            .order_by(order)
            .limit(PAGE_SIZE)
            .offset(PAGE_SIZE * (page - 1))
            .all()
    )


def recent_plays(user, page=1, order='started'):
    if order == 'started':
        order = Play.started.desc()
    elif order == 'finished':
        order = Play.finished.desc()
    elif order == 'name':
        order = Play.game.name.asc()
    elif order == 'rating':
        order = Play.rating.desc()
    elif order == 'completion':
        order = Play.completion.desc()
    else:
        order = None

    return (
        user.plays
            .order_by(order)
            .limit(PAGE_SIZE)
            .offset(PAGE_SIZE * (page - 1))
            .all()
    )


def search(query):
    results = (
        Game.query
            .filter_by(name=query.strip())
            .order_by(Game.released.desc())
            .all()
    )

    fuzzy = (
        Game.query
            .filter(Game.name.like('%' + query.replace(' ', '%') + '%'))
            .order_by(Game.name.asc())
            .all()
    )

    for game in fuzzy:
        if len(results) >= PAGE_SIZE: break
        if game not in results: results.append(game)

    return results


# When searching for a game from the search box, search games in the DB first,
# then have a separate section with Giant Bomb results. Have a button that
# will import (via AJAX) the GB result into the DB.

# Display GB logo, link, and thanks on any page that displays GB content
# (search results and game display, if there is a gb_url)


def search_gb(query):
    results, error = GB.search(query, limit=PAGE_SIZE)

    if error:
        print(error)
    else:
        # TODO: Don't map unless you want them added to the session!
        return map(existing_or_parse_game, results)


def platform_gb(gb_id):
    results, error = GB.platform(gb_id)

    if error:
        print(error)
    else:
        # TODO: Don't map unless you want them added to the session!
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
        # TODO: Don't map unless you want them added to the session!
        return map(parse_gb_platform, results)


def add_game(user, game):
    """
    Adds an existing Game object (e.g., from Giant Bomb) to the database.
    """
    user.games_added.append(game)
    db.session.add(user)
    db.session.add(game)
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
        # TODO: Don't parse (?) unless you want them added to the session!
        print('Parsing game...')
        game = existing_or_parse_game(results)
        print('Adding game...')
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
    play = Play(**fields)
    user.plays.append(play)
    db.session.add(user)
    db.session.commit()
    return play


def edit_game():
    pass


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
    # TODO
    pass


def update_platform(platform):
    """
    Update a platform by fetching its data from the Giant Bomb database.
    """
    # TODO
    pass


def edit_play():
    # TODO
    pass


def game_details(id):
    # TODO
    pass


def play_details(id):
    # TODO
    pass


def tag():
    # TODO
    pass
