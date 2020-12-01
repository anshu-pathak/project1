from flask_mail import Mail,Message
from flask import Flask
from celery import Celery

app = Flask(__name__)


# set up celery client
app.config.from_object("config")
app.secret_key = app.config['SECRET_KEY']

# set up celery client
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
mail = Mail(app)

# @client.task
# def send_email(to, subject, template):
#     msg = Message(
#         subject,
#         recipients=[to],
#         html=template,
#         sender="rahul@gmail.com"
#     )
#     mail.send(msg)

@celery.task
def send_email(to, subject, template):
    """ Function to send emails in the background.
    """
    with app.app_context():
        msg = Message(
            subject,
            recipients=[to],
            html=template,
            sender="rahul@gmail.com"
            )      
        mail.send(msg)