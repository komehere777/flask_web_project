from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from apps.personal.models import Wishlist
from apps.app import db
from apps.crud.models import User
from apps.personal.forms import UserForm
from flask_login import login_required, current_user

personal = Blueprint('personal', __name__, template_folder='templates', static_folder='static')

@personal.route('/')
@login_required
def index():
    user = current_user
    wishlist_items = Wishlist.query.filter_by(user_id=user.id).all()
    return render_template('personal/index.html', user=user, wishlist_items=wishlist_items)

@personal.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_user():
    user = current_user
    form = UserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        if form.password.data:
            user.password_hash = generate_password_hash(form.password.data)
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('personal.index'))
    return render_template('personal/edit_user.html', form=form, user=user)
