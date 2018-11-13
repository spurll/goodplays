from flask import render_template, flash, redirect, session, url_for, request
from flask_login import login_user, logout_user, current_user, login_required

from goodplays import app, db, lm
from goodplays.forms import LoginForm
from goodplays.models import User, Game, Platform, Play, Tag
from goodplays.authenticate import authenticate
from goodplays import controller


@app.route('/')
@app.route('/index')
def index():
    return redirect(url_for('latest'))


@app.route('/search')
def search():
    """
    Search the DB for a game.
    """
    query = request.args.get('query')

    # TODO add a default.png in static/ with a question mark icon

    games = controller.search(query)

    if not games:
        flash("Games don't exist. Good riddance.")

    return render_template(
        "list.html",
        title="Search Results",
        user=current_user,
        games=games
    )


@app.route('/latest')
def latest():
    """
    Shows the 10 most recent games added to the DB. (Or to GiantBomb's DB?
    Maybe set up a daily task to update this DB? It'll get big...)
    """
    games = controller.games()

    if not games:
        flash("Games don't exist. Good riddance.")

    return render_template(
        "list.html", title="Recently Added", user=current_user, games=games
    )


@app.route('/plays')
@login_required
def plays():
    """
    Displays a user's plays.
    """
    user = current_user
    objects = user.objects

    form = TemplateForm()

    if not objects:
        flash("You don't have any objects.")

    return render_template(
        "view.html", title="View", user=user, form=form, objects=objects
    )


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
            'login.html', title="Log In", form=form, hide_user=True
        )

    if form.validate_on_submit():
        user, message = authenticate(form.username.data, form.password.data)

        if not user:
            flash('Login failed: {}.'.format(message))
            return render_template(
                'login.html', title="Log In", form=form, hide_user=True
            )

        if user and user.is_authenticated:
            db_user = User.query.get(user.id)
            if db_user is None:
                db.session.add(user)
                db.session.commit()

            login_user(user, remember=form.remember.data)

            return redirect(request.args.get('next') or url_for('index'))

    return render_template(
        'login.html', title="Log In", form=form, hide_user=True
    )


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@lm.user_loader
def load_user(id):
    return User.query.get(id)

