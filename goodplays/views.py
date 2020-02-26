from flask import render_template, flash, redirect, session, url_for, request
from flask_login import login_user, logout_user, current_user, login_required

from goodplays import app, db, lm
from goodplays.forms import LoginForm, AddPlayForm, EditPlayForm
from goodplays.models import User, Game, Platform, Play, Tag, Status
from goodplays.authenticate import authenticate
from goodplays import controller


@app.route('/')
@app.route('/index')
def index():
    logged_in = current_user.is_authenticated;
    return redirect(url_for('plays' if logged_in else 'games'))


# TODO: Maybe games not linked to Giant Bomb can only be viewed by the user
# who added them?

# TODO: if game not linked to Giant Bomb, a button to link it

# TODO: Remove "Add" button in search if it's already added!
# Frustratingly difficult to do, since we're using DB models for all.
# Could restructure our models, or add a "shadow" model with the same interface

# TODO: Can delete a game if you're logged in and the game has no plays

# TODO: Whenever tags are displayed, they're links! click on a link to bring up
# all games that have plays that have been tagged with that tag?

# TODO: NEXT NEXT NEXT
# Ability to DELETE A PLAY on the Details page (broken)
# Abiltiy to EDIT A PLAY on the Details page (not implemented)
# Tags not working?


@app.route('/search')
def search():
    """
    Search the DB for a game.
    """
    query = request.args.get('query')

    g = controller.search(query)
    gb = list(controller.search_gb(query))

    if not g and not gb:
        flash("Games don't exist. Good riddance.")

    return render_template(
        'games.html',
        title=f'Search: {query}',
        user=current_user,
        games=g,
        giantbomb=gb
    )


@app.route('/games')
def games():
    """
    Shows the 10 most recent games added to the DB. (Or to GiantBomb's DB?
    Maybe set up a daily task to update this DB? It'll get big...)
    """
    g = controller.games()

    if not g:
        flash("Games don't exist. Good riddance.")

    return render_template(
        'games.html',
        title='Recently Added',
        user=current_user,
        games=g
    )


@app.route('/plays')
@login_required
def plays():
    """
    Displays a user's plays.
    """
    p = controller.plays(current_user)

    # TODO display status via icon with description as alt/title text (maybe
    # make it toggleable by clicking); add this to the game/play view, too!

    if not p:
        flash("Games don't exist. Good riddance.")

    # TODO this might actually need a different template, since it's displaying
    # plays not games
    return render_template(
        'plays.html',
        title='Recently Played',
        user=current_user,
        plays=p
    )


@app.route('/details/<id>')
def details(id):
    """
    Displays a game's details page.
    """
    game = controller.game(id)

    if not game:
        flash(f"Unable to find game with ID {id}.")
        return redirect(url_for('index'))

    return render_template(
        'details.html',
        title=game.name,
        user=current_user,
        game=game,
        add_form=AddPlayForm(),
        edit_form=EditPlayForm(),
        plays=current_user.plays
            .filter_by(game_id=game.id).order_by()
            .order_by(Play.started.desc())
            .all() if current_user.is_authenticated else None
    )


@app.route('/add/<gb_id>')
@login_required
def add(gb_id):
    """
    Adds a game from Giant Bomb.
    """
    game = controller.add_gb(current_user, gb_id)

    if not game:
        flash(f'No game with ID {gb_id} was found in Giant Bomb\'s database.')
        return redirect(url_for('games'))

    return redirect(url_for('details', id=game.id))


@app.route('/add-play/<game_id>', methods=['POST'])
@login_required
def add_play(game_id):
    """
    Adds a play.
    """
    form = AddPlayForm()

    if form.validate_on_submit():
        controller.new_play(
            current_user,
            game_id=game_id,
            started=form.started.data,
            finished=form.finished.data,
            status=form.status.data,
            rating=form.rating.data,
            comments=form.comments.data,
            tags=controller.map_tags(form.tags.data.split(','))
        )
    else:
        print(form.errors)
        flash(form.errors)

    return redirect(url_for('details', id=game_id))


@app.route('/delete-play', methods=['GET'])
@login_required
def delete_play(id):
    """
    Deletes a play.
    """
    play = current_user.plays.get(id)
    game = play.game
    controller.delete_play(play)

    return redirect(url_for('details', id=game.id))


@app.route('/edit-play', methods=['POST'])
@login_required
def edit_play():
    """
    Edits a play.
    """
    pass
    #return redirect(url_for('details', id=play.game.id))


@app.route('/update/<id>')
@login_required
def update(id):
    """
    Updates a game with data from Giant Bomb.
    """
    game = controller.game(id)
    controller.update_game(game)

    if not game:
        flash(f'Unable to update game with ID {id}.')
        return redirect(url_for('games'))

    return redirect(url_for('details', id=game.id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Logs the user in
    """
    if current_user and current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if request.method == 'GET':
        return render_template(
            'login.html', title='Log In', form=form, hide_user=True
        )

    if form.validate_on_submit():
        user, message = authenticate(form.username.data, form.password.data)

        if not user:
            flash(f'Login failed: {message}.')
            return render_template(
                'login.html', title='Log In', form=form, hide_user=True
            )

        if user and user.is_authenticated:
            db_user = User.query.get(user.id)
            if db_user is None:
                db.session.add(user)
                db.session.commit()

            login_user(user, remember=form.remember.data)

            return redirect(request.args.get('next') or url_for('index'))

    return render_template(
        'login.html', title='Log In', form=form, hide_user=True
    )


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@lm.user_loader
def load_user(id):
    return User.query.get(id)

