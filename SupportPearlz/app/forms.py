from flask_wtf import FlaskForm
from wtforms import PasswordField, TextAreaField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    api_key = PasswordField(
        "OpenAI API key",
        validators=[DataRequired(message="Please enter your OpenAI API key.")],
    )


class QuestionForm(FlaskForm):
    question = TextAreaField(
        "Question",
        validators=[
            DataRequired(message="Please type a question."),
            Length(max=800, message="Please keep questions under 800 characters."),
        ],
    )
