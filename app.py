import os
from flask import Flask
from dotenv import load_dotenv

from molcalc.extensions import db
from molcalc.views import main_bp

load_dotenv()

def create_app():
    app = Flask(__name__,
                static_folder='molcalc/static',
                template_folder='molcalc/templates')

    # Load configuration from environment variables
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['GAMESS_RUNGMS'] = os.environ.get('GAMESS_RUNGMS')
    app.config['GAMESS_SCR'] = os.environ.get('GAMESS_SCR')
    app.config['GAMESS_USERSCR'] = os.environ.get('GAMESS_USERSCR')
    app.config['MOLCALC_SCR'] = os.environ.get('MOLCALC_SCR')

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()

    return app
