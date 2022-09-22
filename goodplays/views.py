from flask import render_template, flash, redirect, session, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urljoin
import requests

from goodplays import app, db, lm, controller
from goodplays.models import User, Game, Platform, Play, Tag, Status
from goodplays.authenticate import authenticate
from goodplays.forms import LoginForm, SignupForm, AddPlayForm, EditPlayForm, \
    EditGameForm


@app.route('/')
def index():
    logged_in = current_user.is_authenticated;
    return redirect(url_for('plays' if logged_in else 'games'))


@app.route('/games')
def games():
    sort = request.args.get('sort', 'added')
    page = int(request.args.get('page', '1'))
    search = request.args.get('search')

    if (search):
        g = controller.search(search)
        gb = controller.search_gb(search)
    else:
        g = controller.games(sort, page)
        gb = None

    return render_template(
        'games.html',
        title=(f'Search: {search} | ' if search else '') + 'Goodplays',
        user=current_user,
        games=g,
        giantbomb=gb,
        sort=sort if not search else None,
        page=page,
        search=search,
        more=len(g) == controller.PAGE_SIZE,
        can_add=current_user.is_authenticated
    )


@app.route('/plays')
@login_required
def plays():
    fave = bool(request.args.get('fave'))
    status = Status.coerce(request.args.get('status'))
    group = request.args.get('group')
    page = int(request.args.get('page', '1'))

    p = controller.plays(current_user, fave, status, page)

    statuses = [
        {'name': s, 'pretty': s.pretty(), 'selected': status == s}
        for s in Status.filters()
    ]

    return render_template(
        'plays.html' if not group else 'grouped.html',
        title='Goodplays',
        user=current_user,
        plays=p,
        status=status,
        statuses=statuses,
        fave=fave,
        group=group,
        page=page,
        more=len(p) == controller.PAGE_SIZE
    )


@app.route('/details/<int:id>')
def details(id):
    """
    Displays a game's details page
    """
    game = controller.game(id)

    if not game:
        flash(f"Unable to find game with ID {id}.")
        return redirect(url_for('index'))

    return render_template(
        'details.html',
        title=f'{game.name} | Goodplays',
        user=current_user,
        game=game,
        add_form=AddPlayForm(),
        edit_form=EditPlayForm(),
        plays=controller.game_plays(current_user, game.id),
        hltb=controller.hltb(game),
        can_edit=current_user.is_authenticated,
        can_delete=current_user.is_authenticated and not game.plays.count(),
    )


@app.route('/add')
@login_required
def add():
    """
    Adds a new game to the database.
    """
    name = controller.titlecase(request.args.get('name'))
    game = controller.new_game(current_user, name=name)
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
        hltb_id=game.hltb_id,
        description=game.description,
        released=game.released,
        platforms=[p.id for p in game.platforms]
    )

    if request.method == 'POST' and form.validate_on_submit():
        controller.edit_game(
            game=game,
            name=form.name.data,
            released=form.released.data,
            image_url=form.image_url.data,
            hltb_id=form.hltb_id.data and int(form.hltb_id.data) or None,
            description=form.description.data,
            platforms=controller.map_platforms(form.platforms.data)
        )

        return redirect(url_for('details', id=id))

    elif form.errors:
        flash_errors(form)

    return render_template(
        'edit.html',
        user=current_user,
        title='Edit Game | Goodplays',
        game=game,
        form=form
    )


@app.route('/add/<gb_id>')
@login_required
def add_gb(gb_id):
    """
    Adds a game from Giant Bomb
    """
    game = controller.add_gb(current_user, gb_id)

    if not game:
        flash(f'No game with ID {gb_id} was found in Giant Bomb\'s database.')
        return redirect(url_for('games'))

    return redirect(url_for('details', id=game.id))


@app.route('/fave/<int:id>')
@login_required
def fave(id):
    """
    Favourites a play
    """
    play = controller.play(id)

    if not play:
        flash(f'No play with ID {id} was found.')
        return redirect(request.args.get('next') or url_for('plays'))

    controller.fave(play)

    return redirect(request.args.get('next') or url_for('plays'))


@app.route('/add-play/<int:game_id>', methods=['POST'])
@login_required
def add_play(game_id):
    """
    Adds a play
    """
    form = AddPlayForm()

    if form.validate_on_submit():
        controller.new_play(
            current_user,
            game_id=game_id,
            started=form.started.data,
            finished=form.finished.data,
            status=form.status.data,
            rating=int(form.rating.data) if form.rating.data else None,
            comments=form.comments.data,
            tags=controller.map_tags(form.tags.data.split(',')),
            fave=form.fave.data == 'true'
        )

    else:
        flash_errors(form)

    return redirect(url_for('details', id=game_id))


@app.route('/delete/<int:id>', methods=['GET'])
@login_required
def delete(id):
    """
    Deletes a game
    """
    game = controller.game(id)
    controller.delete_game(game)

    return redirect(url_for('games'))


@app.route('/delete-play', methods=['GET'])
@login_required
def delete_play():
    """
    Deletes a play
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
    Edits a play
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
            rating=int(form.rating.data) if form.rating.data else None,
            comments=form.comments.data,
            tags=controller.map_tags(form.tags.data.split(',')),
            fave=form.fave.data == 'true',
        )

    else:
        flash_errors(form)

    return redirect(url_for('details', id=play.game.id))


@app.route('/import-image/<int:id>')
@login_required
def import_image(id):
    """
    Import's a game's hotlinked cover image
    """
    game = controller.game(id)

    if not game:
        flash(f'Unable to import image for game with ID {id}.')
        return redirect(url_for('games'))

    controller.import_image(game)

    return redirect(url_for('details', id=game.id))


@app.route('/update/<int:id>')
@login_required
def update(id):
    """
    Updates a game with data from Giant Bomb
    """
    game = controller.game(id)
    controller.update_game(game)

    if not game:
        flash(f'Unable to update game with ID {id}.')
        return redirect(url_for('games'))

    return redirect(url_for('details', id=game.id))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if request.method == 'POST' and form.validate_on_submit():
        payload = {
            'id': form.username.data,
            'email': form.email.data,
            'password': form.password.data,
            'name': form.name.data,
            'next': url_for('login', _external=True)
        }

        url = urljoin(request.base_url, '/auth/new')
        r = requests.post(url, json=payload)

        if r.status_code == 200:
            flash('Success! Please check your email to complete signup.')
            return redirect(url_for('login'))

        else:
            flash(f'Signup failed: {r.text}.')

    elif form.errors:
        flash_errors(form)

    return render_template(
        'signup.html',
        title='Sign Up | Goodplays',
        form=form,
        hide_user=True
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Logs the user in
    """
    if current_user and current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if request.method == 'POST' and form.validate_on_submit():
        user, message = authenticate(form.username.data, form.password.data)

        if user and user.is_authenticated:
            db_user = User.query.get(user.id)

            if db_user is None:
                db.session.add(user)
                db.session.commit()

            login_user(user, remember=form.remember.data)

            return redirect(request.args.get('next') or url_for('index'))

        flash(f'Login failed: {message}.')

    return render_template(
        'login.html',
        title='Log In | Goodplays',
        form=form,
        hide_user=True
    )


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@lm.user_loader
def load_user(id):
    return User.query.get(id)


def flash_errors(form):
    for field, messages in form.errors.items():
        label = getattr(getattr(getattr(form, field), 'label'), 'text', '')
        label = label.replace(':', '')
        error = ', '.join(messages)

        message = f'Error in {label}: {error}' if label else 'Error: {error}'

        flash(message)
        print(message)

