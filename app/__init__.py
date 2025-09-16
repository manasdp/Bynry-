from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize the Flask application
app = Flask(__name__)

# Configure the database connection
# In a real application, this would come from a configuration file or environment variables
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stockflow.db' # Using SQLite for simplicity
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy database object
db = SQLAlchemy(app)

# Import routes and models at the end to avoid circular import errors
# These modules need `app` and `db` to be defined first
from app import routes, models
