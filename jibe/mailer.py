"""
This script is used to send emails
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from os.path import dirname, join
import os


"""
A mailer component used to send emails
Modified from the Serapis Project
"""

DEFAULT_FROM = os.environ['DEFAULT_FROM']
DEFAULT_SERVER = os.environ['DEFAULT_SERVER']


def __init__(self):
    """Returns mailer object
    """
    self._cfg = {}
    self._cfg.setdefault("server", self.DEFAULT_SERVER)
    self._cfg.setdefault("from", self.DEFAULT_FROM)


def send(self, recipients, subject, text):
    """ Sends email to recipients
    :param list recipients : recipients of email
    :param string subject : subject of the email
    :param: bool attachments : bool to attach images
    :pram string text: text of the email
    """
    sender = self._cfg["from"]
    msg = MIMEMultipart('related')
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    server = smtplib.SMTP(self._cfg["server"])
    part = MIMEText(text, 'html', 'utf-8')
    msg.attach(part)

    # Attach images to the email
    image_specs = [
        ('../images/blocker.png', '<blocker_priority_image>'),
        ('../images/critical.png', '<critical_priority_image>'),
        ('../images/major.png', '<major_priority_image>'),
        ('../images/minor.png', '<minor_priority_image>'),
        ('../images/trivial.png', '<trivial_priority_image>')
    ]

    for spec in image_specs:
        with open(join(dirname(__file__), spec[0]),
                  'rb') as fp:
            image = MIMEImage(fp.read(), _subtype='png')
            image.add_header('Content-ID', spec[1])
            msg.attach(image)

    server.sendmail(sender, recipients, msg.as_string())
