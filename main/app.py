from flask import Flask
import os
import sys

# Add parent directory to path so we can import routes
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import SECRET_KEY
from routes.auth import auth_bp
from routes.user import user_bp
from routes.admin import admin_bp

# Get the parent directory to locate templates folder
basedir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(os.path.dirname(basedir), 'templates')

app = Flask(__name__, template_folder=template_dir)
app.secret_key = SECRET_KEY

app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)

if __name__ == "__main__":
    app.run(debug=True)
