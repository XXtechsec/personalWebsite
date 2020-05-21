import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = "False"
    PASSWORD = 'password'
    IMAGE_UPLOADS = "/Users/tony/Documents/personalWebsite/base/static/img/uploads"
    ALLOWED_IMAGE_EXTENSIONS = ["JPEG", "JPG", "PNG", "GIF"]
    MAIL_SERVER = 'smtp.sendgrid.net'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "apikey"
    MAIL_PASSWORD = os.environ.get('SENDGRID_API_KEY')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

