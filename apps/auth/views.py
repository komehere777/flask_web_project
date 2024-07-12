from apps.app import db
from apps.auth.forms import SignUpForm, LoginForm
from apps.crud.models import User
from flask import Blueprint, render_template, flash, url_for, redirect, request, session
from flask_login import login_user, logout_user
from flask import current_app
auth = Blueprint('auth', __name__, template_folder='templates', static_folder='static')


# 애플리케이션 요청 처리 전에 관리자 계정 생성
@auth.before_request
def create_admin():  # 관리자 계정이 없으면 생성
    with current_app.app_context():
        if not User.query.filter_by(username="admin").first():
            admin = User(username="admin", is_admin=True)
            admin.password = "admin"
            db.session.add(admin)
            db.session.commit()


@auth.route('/')
def index():
    return render_template('auth/index.html')


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )
        if user.is_duplicate_email():
            flash('이미 가입된 이메일 주소입니다.')
            return redirect(url_for('auth.signup'))
        db.session.add(user)
        db.session.commit()
        login_user(user)
        # next_ = request.args.get('next')
        # if next_ is None or not next_.startswith('/'):
        #     next_ = url_for('crud.users')
        # return redirect(next_)
    return render_template('auth/signup.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            session["user_id"] = user.id
            session["username"] = user.username
            session["is_admin"] = user.is_admin
            flash("Login successful!", "success")
            return redirect(url_for('crud.users'))
        
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for('crud.users'))
        flash('이메일 또는 비밀번호가 올바르지 않습니다.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
