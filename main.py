from app import app, db
from agri_features_clean import register_agri_features

register_agri_features(app, db)

with app.app_context():
    db.create_all()
    app.extensions["agri_seed"]()

application = app
