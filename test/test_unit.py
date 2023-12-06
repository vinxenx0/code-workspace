# test_app.py

import unittest
from flask import current_app
from app import app, db
from app.models.user_model import User

class TestApp(unittest.TestCase):
    def setUp(self):
        with app.app_context():
            app.config['TESTING'] = True
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
            self.app = app.test_client()
            db.create_all()

            # Simulate a user login for authenticated routes
            with self.app.session_transaction() as session:
                user = User(username='test__user', email='test__user@test.com', password='password123')
                db.session.add(user)
                db.session.commit()
                session['user_id'] = user.id

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_home_route_authenticated(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        

    def test_home_route_unauthenticated(self):
        # Clear the session to simulate an unauthenticated user
        with self.app.session_transaction() as session:
            session.clear()

        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 401)
       

    def test_user_model(self):
        user = User(username='test', email='test@test.com', password='testpassword')
        db.session.add(user)
        db.session.commit()

        retrieved_user = User.query.filter_by(username='test').first()
        self.assertIsNotNone(retrieved_user)
      

if __name__ == '__main__':
    unittest.main()
