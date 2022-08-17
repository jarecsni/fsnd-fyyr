import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database - provide your own DB URL!
SQLALCHEMY_DATABASE_URI = 'postgresql://[user]:[pw]]@localhost:5432/[db]'
