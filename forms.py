from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms.validators import DataRequired, Length

           ###バリデータクラス定義###
class PersonalInfoForm(FlaskForm):
    username = StringField('ユーザー名', validators=[DataRequired(), Length(min=3, max=50)])
    email = EmailField('メールアドレス', validators=[DataRequired(), Email(message='有効なメールアドレスを入力してください')])
    password = PasswordField('パスワード',validators=[DataRequired(),Length(min=6, max=12, message='パスワードの長さは6文字以上12文字以内です')])
    confirm_password = PasswordField('パスワード確認 ', validators=[DataRequired(),EqualTo('password', 'パスワードが一致しません')])
    height = IntegerField('身長', validators=[DataRequired()])
    weight = IntegerField('体重', validators=[DataRequired()])
    submit = SubmitField('送信')

            ###ログイン用のフォーム###
class LoginForm(FlaskForm):
    email = StringField('メールアドレス', validators=[DataRequired()])
    password = PasswordField('パスワード', validators=[DataRequired()])
    submit = SubmitField('ログイン')