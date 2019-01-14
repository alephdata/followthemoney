import os
from normality import slugify

PROJECT_NAME = 'Follow the Money'
PROJECT_NAME = os.environ.get('INTEGRATE_PROJECT_NAME', PROJECT_NAME)

DATABASE_URI = 'sqlite:///integrate.sqlite3'
DATABASE_URI = os.environ.get('INTEGRATE_DATABASE_URI', DATABASE_URI)
DATABASE_PREFIX = os.environ.get('INTEGRATE_DATABASE_PREFIX', 'ftm')
DATABASE_PREFIX = slugify(DATABASE_PREFIX, sep='_')

QUORUM = int(os.environ.get('INTEGRATE_QUORUM', 1))