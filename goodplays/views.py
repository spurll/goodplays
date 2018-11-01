from flask import render_template, flash, redirect, session, url_for, request
from flask_login import login_user, logout_user, current_user, login_required

from goodplays import app, db, lm
from goodplays.forms import LoginForm
from goodplays.models import User, Game, Platform, Play, Tag
from goodplays.authenticate import authenticate


@app.route('/')
@app.route('/index')
def index():
    return redirect(url_for("latest"))


@app.route('/latest')
def latest():
    """
    Shows the 10 most recent games added to the DB. (Or to GiantBomb's DB?
    Maybe set up a daily task to update this DB? It'll get big...)
    """
    user = current_user
    games = [] #Game.query. # TODO 10 latest!

    # TODO Show most recent 10 games added to the DB.

    if not games:
        flash("Games don't exist. Good riddance. Thanks, Tauriq!")

    return render_template(
        "latest.html", title="Latest Games", user=user, links=None, games=games
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
        "view.html", title="View", user=user, links=None, form=form,
        objects=objects
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Logs the user in
    """
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if request.method == 'GET':
        return render_template('login.html', title="Log In", form=form)

    if form.validate_on_submit():
        user, message = authenticate(form.username.data, form.password.data)

        if not user:
            flash('Login failed: {}.'.format(message))
            return render_template('login.html', title='Log In', form=form)

        if user and user.is_authenticated:
            db_user = User.query.get(user.id)
            if db_user is None:
                db.session.add(user)
                db.session.commit()

            login_user(user, remember=form.remember.data)

            return redirect(request.args.get('next') or url_for('index'))

    return render_template('login.html', title="Log In", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@lm.user_loader
def load_user(id):
    return User.query.get(id)

