import os
import connexion
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

basedir = os.path.abspath(os.path.dirname(__file__))

# Create the connexion application instance
connexion_app = connexion.App(__name__, specification_dir=basedir)

# Get the underlying Flask app instance
app = connexion_app.app

db_client = os.getenv("DB_CLIENT")
db_name = os.getenv("DB_NAME")
db_host = os.getenv("DB_HOST")
db_username = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")
db_port = os.getenv("DB_PORT")
db_connection_string = "%s://%s:%s@%s:%s/%s" % (db_client, db_username, db_password, db_host, db_port, db_name)

# Configure the SqlAlchemy part of the app instance
app.config["SQLALCHEMY_ECHO"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = db_connection_string
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Create the SqlAlchemy db instance
db = SQLAlchemy(app)

@app.before_first_request
def create_tables():
    db.create_all()
    
# Initialize Marshmallow
ma = Marshmallow(app)
