from goodplays import app, db
from goodplays.models import User, Game, Play, Platform, Tag


PAGE_SIZE = app.config.get('PAGE_SIZE', 20)


def platforms():
    return Platforms.all()


def games(page=1, order='added'):
    if order == 'added':
        order = Game.added.desc()
    elif order == 'name':
        order = Game.name.asc()
    elif order == 'year':
        order = Game.year.desc()
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
        .filter_by(name=query)
        .order_by(Game.year.desc())
        .all()
    )

    # TODO: THIS APPEARS TO BE BROKEN
    fuzzy = (
        Game.query
        .filter(Game.name.like(query.replace(' ', '%') + '%'))
        .order_by(Game.name.asc())
        .all()
    )

    for game in fuzzy:
        if len(results) >= PAGE_SIZE: break
        if game not in results: results.append(game)

    return results


def search_gb(query):
    pass


def add_game(user, **fields):
    game = Game(**fields)
    user.games_added.append(game)
    db.session.commit()
    return game


def add_play(user, **fields):
    play = Play(**fields)
    user.plays.append(play)
    db.session.commit()
    return play


def edit_game():
    pass


def edit_play():
    pass


def game_details(id):
    pass


def play_details(id):
    pass


def tag():
    pass


# TODO: Include rate limiting in Giant Bomb searches (no more than 200 searches
# per hour)

# When searching for a game from the search box, search games in the DB first,
# then have a separate section with Giant Bomb results. Have a button that
# will import (via AJAX) the GB result into 

# Display GB logo, link, and thanks on any page that displays GB content
# (search results and game display, if there is a gb_url)

#def add_game(
