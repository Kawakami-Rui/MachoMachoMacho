from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms.validators import DataRequired, Length

           ###バリデータクラス定義###
class PersonalInfoForm(FlaskForm):
    username = StringField('ユーザー名', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('メールアドレス', validators=[DataRequired(), Email()])
    password = PasswordField('パスワード', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('パスワード確認用', validators=[
        DataRequired(), EqualTo('password', message='パスワードが一致しません')])
    height = StringField('身長', validators=[DataRequired()])
    weight = StringField('体重', validators=[DataRequired()])
    submit = SubmitField('送信')

            ###ログイン用のフォーム###
class LoginForm(FlaskForm):
    email = StringField('メールアドレス', validators=[DataRequired()])
    password = PasswordField('パスワード', validators=[DataRequired()])
    submit = SubmitField('ログイン')