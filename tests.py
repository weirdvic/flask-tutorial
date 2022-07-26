from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Post

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(username='alice')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_avatar(self):
        u = User(username='alice', email='alice@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                        'c160f8cc69a4f0bf2b0362752353d060'
                                        '?d=identicon&s=128'))

    def test_follow(self):
        u1 = User(username='alice', email='alice@example.com')
        u2 = User(username='bob', email='bob@example.com')
        db.session.add_all([u1, u2])
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'bob')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'alice')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_follow_posts(self):
        # create four users
        u1 = User(username='alice', email='alice@example.com')
        u2 = User(username='bob', email='bob@example.com')
        u3 = User(username='carol', email='carol@example.com')
        u4 = User(username='dave', email='dave@example.com')
        db.session.add_all([u1, u2, u3, u4])

        # create four posts
        now = datetime.utcnow()
        p1 = Post(body="post from alice", author=u1,
                  timestamp=now + timedelta(seconds=1))
        p2 = Post(body="post from bob", author=u2,
                  timestamp=now + timedelta(seconds=4))
        p3 = Post(body="post from carol", author=u3,
                  timestamp=now + timedelta(seconds=3))
        p4 = Post(body="post from dave", author=u4,
                  timestamp=now + timedelta(seconds=2))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # setup the followers
        u1.follow(u2)  # alice follows bob
        u1.follow(u4)  # alice follows dave
        u2.follow(u3)  # bob follows carol
        u3.follow(u4)  # carol follows dave
        db.session.commit()

        # check the followed posts of each user
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])
    
    def test_jwt(self):
        u1 = User(username='alice', email='alice@example.com')
        db.session.add(u1)
        db.session.commit()
        token=u1.get_reset_password_token()
        u2 = User.verify_reset_password_token(token)
        self.assertEqual(u1,u2)




if __name__ == '__main__':
    unittest.main(verbosity=2)
