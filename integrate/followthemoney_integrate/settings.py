import os
from normality import slugify

DATABASE_URI = 'sqlite:///integrate.sqlite3'
DATABASE_URI = os.environ.get('INTEGRATE_DATABASE_URI', DATABASE_URI)
DATABASE_PREFIX = os.environ.get('INTEGRATE_DATABASE_PREFIX', 'ftm')
DATABASE_PREFIX = slugify(DATABASE_PREFIX, sep='_')
