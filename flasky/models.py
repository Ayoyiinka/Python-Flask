from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flasky import db, login, app
from flask_login import UserMixin
from hashlib import md5
import jwt
from time import time
from flasky.search import add_to_index, remove_from_index, query_index

class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
                db.case(when, value=Post.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
                'add': [obj for obj in session.new if isinstance(obj, cls)],
                'update': [obj for obj in session.dirty if isinstance(obj, cls)],
                'delete': [obj for obj in session.deleted if isinstance(obj, cls)]
            }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            add_to_index(cls.__tablename__, obj)
        for obj in session._changes['update']:
            add_to_index(cls.__tablename__, obj)
        for obj in session._changes['delete']:
            remove_from_inde(cls.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

#Since this is an auxillary table that has no data other than the foreignkeys,
#that is why it is created without an associated model class.
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(120))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship('User', secondary=followers,
            primaryjoin=(followers.c.follower_id == id),
            secondaryjoin=(followers.c.followed_id == id),
            backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
                #secondary :: configures the association table
                #primaryjoin :: indicates the condition that links the left-side entity and the association table
                #secondaryjoin :: indicates the condition that links the right-side entity and the association table
    def __repr__(self):
        return "<User {}>".format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    #the MD5 support in Python works on bytes and not on strings, therefore I encode the string as bytes before passing it on to the hash function.
    def avatar(self, size): #the gravatar service treats all emails as lowercase
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size) #hexdigest helps to get a string representation of the hash

    #HELPER METHODS
    def follow(self, user):
        if not self.is_following(user): #prevents duplication in the database
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user): #prevents duplication in the database
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
#filter takes an expression that is sent directly to the database, while filter_by takes keyword arguments.

    def followed_posts(self):
        followed = Post.query.join(
                    followers, (followers.c.followed_id == Post.user_id)).filter(
                    followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600): #600 seconds
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in}, #this doesn't generate an encrypted token, what makes the token secure is that the payload {} is signed
                            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8') # converted the token (byte) to a string with the decode method

    @staticmethod #this is going to be the function to be called when the user clicks on the link and sends the token back to us
    def verify_reset_password(token):
        try:
            id = jwt.decode(token , app.config['SECRET_KEY'],
                        algorithms=['HS256'])['reset_password']
        except:
            return None
        return User.query.get(id)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Post(SearchableMixin, db.Model):
    __searchable__ = ['body']
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow) #hence the function utcnow is called every time a post is created
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))

    def __repr__(self):
        return "<Post {}>".format(self.body)

db.event.listen(db.session, 'before_commit', Post.before_commit)
db.event.listen(db.session, 'after_commit', Post.after_commit)
