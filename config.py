import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # For sqlite:
    db_name = 'test.db'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # For heroku db:
    # db_username = ''
    # db_password = ''
    # db_host     = ''
    # db_name     = ''
    # SQLALCHEMY_DATABASE_URI = 'mysql://{}:{}@{}/{}'.format(db_username,
    #                                                        db_password,
    #                                                        db_host,
    #                                                        db_name)


class ProdConfig(Config):
    pass


class DevConfig(Config):
    DEBUG = True