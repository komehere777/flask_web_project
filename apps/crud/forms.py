from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email
from wtforms.fields import EmailField


class UserForm(FlaskForm):
    username = StringField('사용자명', validators=[DataRequired(message="사용자명은 필수입니다."), Length(max=30, message="30자 이내로 입력해주세요.")])
    email = EmailField('메일주소', validators=[DataRequired(message='메일 주소는 필수입니다.'), Email(message='메일 주소 형식이 아닙니다.')])
    password = PasswordField('비밀번호', validators=[DataRequired(message='비밀번호는 필수입니다.')])
    submit = SubmitField('신규 등록')