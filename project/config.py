SECRET_KEY = 'very_very_secure_and_secret'
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Flask-Mail
MAIL_SERVER ='smtp.mailtrap.io'
MAIL_PORT = 2525
MAIL_USE_TLS = True
MAIL_USERNAME = 'ddaba4be48159d'
MAIL_PASSWORD = 'e521af3933c242'

# app.config['MAIL_SERVER']='smtp.mailtrap.io'
# app.config['MAIL_PORT'] = 2525
# app.config['MAIL_USERNAME'] = 'ddaba4be48159d'
# app.config['MAIL_PASSWORD'] = 'e521af3933c242'
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = False