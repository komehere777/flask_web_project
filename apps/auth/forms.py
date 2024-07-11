from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email


class SignUpForm(FlaskForm):
    username = StringField('사용자명', validators=[DataRequired(message="사용자명은 필수입니다."), Length(max=30, message="30자 이내로 입력해주세요.")])
    email = StringField('이메일', validators=[DataRequired(message='이메일은 필수입니다.'), Email(message='이메일 주소 형식이 아닙니다.')])
    password = PasswordField('비밀번호', validators=[DataRequired(message='비밀번호는 필수입니다.')])
    submit = SubmitField('신규 등록')


class LoginForm(FlaskForm):
    email = StringField('이메일', validators=[DataRequired(message='이메일은 필수입니다.'), Email(message='이메일 주소 형식이 아닙니다.')])
    password = PasswordField('비밀번호', validators=[DataRequired(message='비밀번호는 필수입니다.')])
    submit = SubmitField('로그인')