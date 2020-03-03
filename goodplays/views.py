from flask import render_template, flash, redirect, session, url_for, request
from flask_login import login_user, logout_user, current_user, login_required

from goodplays import app, db, lm
from goodplays.forms import LoginForm, AddPlayForm, EditPlayForm, EditGameForm
from goodplays.models import User, Game, Platform, Play, Tag, Status
from goodplays.authenticate import authenticate
from goodplays import controller


@app.route('/')
@app.route('/index')
def index():
    logged_in = current_user.is_authenticated;
    return redirect(url_for('plays' if logged_in else 'games'))


@app.route('/search')
def search():
    """
    Search the DB for a game.
    """
    query = request.args.get('query')

    g = controller.search(query)
    gb = controller.search_gb(query)

    return render_template(
        'games.html',
        title=f'Search: {query}',
        user=current_user,
        search=query,
        games=g,
        giantbomb=gb
    )


@app.route('/games')
def games():
    """
    Shows the 20 most recent games added to the DB.
    """
    sort = request.args.get('sort', 'added')
    page = int(request.args.get('page', '1'))

    g = controller.games(sort, page)

    return render_template(
        'games.html',
        title='Games',
        user=current_user,
        games=g,
        sort=sort,
        page=page
    )


@app.route('/plays')
@login_required
def plays():
    """
    Displays a user's 20 most recent plays.
    """
    status = Status.coerce(request.args.get('status'))
    page = int(request.args.get('page', '1'))

    p = controller.plays(current_user, status, page)

    statuses = [
        {'name': s, 'pretty': s.pretty(), 'selected': status == s}
        for s in Status.in_use()
    ]

    return render_template(
        'plays.html',
        title='Plays',
        user=current_user,
        plays=p,
        status=status,
        statuses=statuses,
        page=page
    )


@app.route('/details/<int:id>')
def details(id):
    """
    Displays a game's details page.
    """
    game = controller.game(id)

    # TODO: If logged in, show edit button
    # TODO: If logged in and the game has no plays, show delete button

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
        plays=controller.game_plays(current_user, game.id)
    )


@app.route('/add')
@login_required
def add():
    """
    Adds a new game to the database.
    """
    game = controller.new_game(current_user)
    return redirect(url_for('edit', id=game.id))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    Adds a new game to the database.
    """
    game = controller.game(id)

    # Initialize with current data, if any
    form = EditGameForm(
        name=game.name,
        image_url=game.image_url,
        description=game.description,
        released=game.released,
        platforms=[p.id for p in game.platforms]
    )

    if form.validate_on_submit():
        controller.edit_game(
            game=game,
            name=form.name.data,
            released=form.released.data,
            image_url=form.image_url.data,
            description=form.description.data,
            platforms=controller.map_platforms(form.platforms.data)
        )

        return redirect(url_for('details', id=id))

    else:
        print(form.errors)
        flash(form.errors)

    return render_template(
        'edit.html',
        user=current_user,
        title='Edit Game',
        game=game,
        form=form
    )


@app.route('/add/<gb_id>')
@login_required
def add_gb(gb_id):
    """
    Adds a game from Giant Bomb.
    """
    game = controller.add_gb(current_user, gb_id)

    if not game:
        flash(f'No game with ID {gb_id} was found in Giant Bomb\'s database.')
        return redirect(url_for('games'))

    return redirect(url_for('details', id=game.id))


@app.route('/add-play/<int:game_id>', methods=['POST'])
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
def delete_play():
    """
    Deletes a play.
    """
    id = int(request.args.get('id'))
    play = current_user.plays.filter_by(id=id).one()
    game = play.game
    controller.delete_play(play)

    return redirect(url_for('details', id=game.id))


@app.route('/edit-play', methods=['POST'])
@login_required
def edit_play():
    """
    Edits a play.
    """
    form = EditPlayForm()
    id = int(form.id.data)
    play = current_user.plays.filter_by(id=id).one()

    if form.validate_on_submit():
        controller.edit_play(
            play,
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

    return redirect(url_for('details', id=play.game.id))


@app.route('/update/<int:id>')
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
        return render_template('login.html', title='Log In', form=form,
            hide_user=True)

    if form.validate_on_submit():
        user, message = authenticate(form.username.data, form.password.data)

        if not user:
            flash(f'Login failed: {message}.')
            return render_template('login.html', title='Log In', form=form,
                hide_user=True)

        if user and user.is_authenticated:
            db_user = User.query.get(user.id)
            if db_user is None:
                db.session.add(user)
                db.session.commit()

            login_user(user, remember=form.remember.data)

            return redirect(request.args.get('next') or url_for('index'))

    return render_template('login.html', title='Log In', form=form,
        hide_user=True)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@lm.user_loader
def load_user(id):
    return User.query.get(id)

