import os


# Database
DATABASE = {'default': os.environ['DATABASE_URL']}

SCORE_SERVICE = os.environ.get('SCORE_SERVICE')
SCORE_KEY = os.environ.get('SCORE_KEY')
