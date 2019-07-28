from flasky import app, db
from flasky.models import User, Post
from flasky import cli

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}
