import requests

from email_message import EmailMessage
from services.abstract import EmailService
from exceptions import *


class MailgunEmailService(EmailService):
    name = "mailgun"

    def __init__(self, domain, api_key, priority=0):
        self.email_domain = domain
        self.api_key = api_key
        self.api_endpoint = "https://api.mailgun.net/v3/{}".format(domain)
        self.priority = priority

    def send_email(self, email_message: EmailMessage):

        post_req_payload = {"to": ",".join(email_message.to_recipients),
                            "subject": email_message.subject,
                            # "text": "{}\nINFO: Sent via Mailgun Email Service".format(email_message.raw_text_body)
                            "text": "{}".format(email_message.raw_text_body)
                            }

        if email_message.from_name is not None:
            post_req_payload["from"] = "{} <{}>".format(email_message.from_name, email_message.from_email)
        else:
            post_req_payload["from"] = email_message.from_email

        if email_message.to_cc is not None and len(email_message.to_cc) > 0:
            post_req_payload["cc"] = ",".join(email_message.to_cc)

        if email_message.to_bcc is not None:
            post_req_payload["bcc"] = email_message.to_bcc

        if email_message.html_body is not None:
            post_req_payload["html"] = email_message.html_body

        resp = requests.post("{}/messages".format(self.api_endpoint), auth=('api', self.api_key), data=post_req_payload)

        if resp.status_code == 200:
            return True
        elif resp.status_code in [401]:
            raise InvalidAPIKeyException(self.name)
        elif resp.status_code in [400, 402, 404, 500, 502, 503, 504]:
            raise GenericEmailRoutingError
