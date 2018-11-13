from goodplays import app, db
from goodplays.models import User, Game, Play, Platform, Tag


PAGE_SIZE = app.config.get('PAGE_SIZE', 20)


def game2row(game):
    return [game.id, str(game), game.art_uri, game.rating, game.platforms]


def gb2row(game):
    pass


def play2row(play):
    return [
        play.id,
        str(play.game),
        play.game.art_uri,
        play.rating,
        play.game.platforms,
        play.started,
        play.finished,
        play.completion,
        play.completed
    ]


def recent_games(page=1):
    return map(
        game2row,
        Game.query
            .order_by(Game.added.desc())
            .limit(PAGE_SIZE)
            .offset(PAGE_SIZE * (page - 1))
            .all()
    )


def recent_plays(user, page=1):
    return map(
        play2row,
        user.plays
            .order_by(Play.started.desc())
            .limit(PAGE_SIZE)
            .offset(PAGE_SIZE * (page - 1))
            .all()
    )


def search(query):
    results = Game.query.filter_by(name=query).order_by(Game.year.desc()).all()
    fuzzy = Game.query
        .filter(Game.name.like(query.replace(' ', '%') + '%'))
        .all()

    for game in fuzzy:
        if len(results) >= PAGE_SIZE: break
        if game not in results: results.append(game)

    return map(game2row, results)


def search_gb(query):
    pass


def add():
    pass


def add_gb():
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
# then have a separate section with GiantBomb results. Have a button that
# will import (via AJAX) the GB result into 

# Display GB logo, link, and thanks on any page that displays GB content
# (search results and game details page, if there is a gb_uri)

#def add_game(
