# run.py
from app.models import User
from app.views import app, db
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

migrate = Migrate(app, db)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Añadir el usuario admin si no existe
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', password=generate_password_hash('admin', method='pbkdf2:sha256'))
            db.session.add(admin)
            db.session.commit()

    app.run(debug=True)