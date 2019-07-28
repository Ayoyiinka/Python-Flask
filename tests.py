from datetime import datetime, timedelta
import unittest
from flasky import app, db
from flasky.models import User, Post

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://' #ensures that we use a different database from the one used during development
        db.create_all() #since for unit tests, we are going to always start from an empty database, then we can use the db.create_all() method from
                        #sqlalchemy to create all the tables from scratch. However, when we are working with the database from development and
                        #production, we used the flask migration framework to make changes to the database.
    def tearDown(self):
        db.session.remove()
        db.drop_all()   #removes all the table after every test.

#the remaining methods test features of the User model and they are recognised by the unit testing framework because
#they start with test_, tests run a particular opertaion and check the result if they are the expected ones by using assert____
#there are assert calls to check for different types of conditions.
    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_avatar(self):
        u = User(username='john', email='john@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                        'd4c74594d841139328695756648b6bd6'
                                        '?d=identicon&s=128'))

    def test_follow(self):
        u1 = User(username='john', email='john@example.come')
        u2 = User(username='susan', email='susan@example.come')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u2.followed.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'susan')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'john')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_followed_posts(self):
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        u3 = User(username='ayo', email='ayo@example.com')
        u4 = User(username='ore', email='ore@example.com')
        db.session.add_all([u1, u2, u3, u4])

        now = datetime.utcnow()
        p1 = Post(body='post from john', author=u1, timestamp=now + timedelta(seconds=1))
        p2 = Post(body='post from susan', author=u2, timestamp=now + timedelta(seconds=4))
        p3 = Post(body='post from ayo', author=u3, timestamp=now + timedelta(seconds=3))
        p4 = Post(body='post from ore', author=u4, timestamp=now + timedelta(seconds=2))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        u1.follow(u2)
        u1.follow(u4)
        u2.follow(u3)
        u3.follow(u4)
        db.session.commit()

        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])

if __name__ == '__main__':
    unittest.main(verbosity=2)
