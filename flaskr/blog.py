from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.models import db, Post
from flaskr.forms import PostAddForm

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    posts = Post.query.all()
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """Handle post creation. """
    form = PostAddForm()

    if form.validate_on_submit():
        try:
            post = Post(
                title=form.title.data,
                body=form.body.data,
            )
            db.session.add(post)
            db.session.commit()
        except(e):
            db.session.rollback()
            flash(f"Something went wrong, here's your error: {e}", 'danger')
            return render_template('blog/create.html', form=form)  # or any other appropriate response
        
        flash("Post successfully created.", 'success')

        return redirect(url_for('blog.index'))
    else:
        return render_template('blog/create.html', form=form)

def get_post(id, check_author=True):
    post = Post.query.get_or_404(id)

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post.author_id != g.user.id:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = Post.query.get_or_404(id)
    form = PostAddForm()

    if form.validate_on_submit():
        try:
            post.title=form.title.data,
            post.body=form.body.data,
            
            db.session.commit()
        except(e):
            db.session.rollback()
            flash(f"Something went wrong, here's your error: {e}", 'danger')
            return render_template('blog/create.html', form=form)  # or any other appropriate response
        
        flash("Post successfully updated.", 'success')

        return redirect("/blog.index")
    else:
        return render_template('blog/update.html', form=form)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.commit()
    return redirect(url_for('blog.index'))


