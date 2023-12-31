import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.models import db, User

from flaskr.forms import UserAddForm, LoginForm

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Handle user signup. """
    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
            )
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            flash(f"Something went wrong, here's your error{e}", 'danger')
            return render_template('auth/register.html', form=form)
        
        flash("Username successfully created.", 'success')

        return redirect(url_for("auth.login"))
    else:
        return render_template('auth/register.html', form=form)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(form.username.data, form.password.data)

        if user:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('index'))

        flash("Invalid credentials.", 'danger')

    return render_template('auth/login.html', form=form)

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get_or_404(user_id)

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view