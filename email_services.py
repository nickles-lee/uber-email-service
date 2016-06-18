import json
import requests
import sendgrid
import sendgrid.helpers.mail
import time
from abc import ABCMeta, abstractmethod

from email_message import EmailMessage

email_config = json.loads(open('config.json', 'r').read())


class RateLimitException(Exception):
    def __init__(self, limited_service):
        self.limited_service = limited_service

    def __str__(self):
        return "[EXCEPT] Rate Limit on {} hit".format(self.limited_service)


class InvalidAPIKeyException(Exception):
    def __init__(self, service):
        self.service = service

    def __str__(self):
        return "[EXCEPT] API Key Error on {} ".format(self.service)


class MissingAPIKeyException(Exception):
    def __init__(self, service):
        self.service = service

    def __str__(self):
        return "[EXCEPT] No API Key for {} ".format(self.service)


class MismatchedEmailDomainException(Exception):
    def __init__(self, domain):
        self.service = domain

    def __str__(self):
        return "[EXCEPT] Mismatched domain specified: {} ".format(self.service)


def validate_send_email(msg: EmailMessage) -> bool:
    return msg.from_email.split("@").get(1) == email_config.get("email_domain")


class EmailService:
    __metaclass__ = ABCMeta

    name = "Undefined service"
    priority = 0
    simulating_failure = False
    rate_limit_msg_count = -1
    rate_limit_window_seconds = -1
    sent_timestamps = []
    supports_cc = False
    supports_bcc = False

    @abstractmethod
    def send_email(self, email_message):
        pass

    def set_priority(self, priority_value):
        self.priority = priority_value

    def set_service_rate_limit(self, msg_count, seconds):
        self.rate_limit_msg_count = msg_count
        self.rate_limit_window_seconds = seconds
        self.sent_timestamps = filter(lambda x: time.time() - x < seconds, self.sent_timestamps)

    # Check if rate limit on service is in effect, clearing timestamp list only if the rate limiter potentially
    # triggers. Has the advantage of having lower amortised time cost, but may result in "lag spikes" if a large
    # rate limit window is hit.
    def check_if_rate_limited(self):
        if self.rate_limit_msg_count < 0:
            return False
        elif len(self.sent_timestamps) < self.rate_limit_msg_count:
            return False
        else:
            self.sent_timestamps = filter(lambda x: time.time() - x < self.rate_limit_window_seconds,
                                          self.sent_timestamps)
            if len(self.sent_timestamps) < self.rate_limit_msg_count:
                return False
            else:
                return True

    def toggle_failure_mode(self):
        self.simulating_failure = not self.simulating_failure
        return self.simulating_failure


class DummyEmailService(EmailService):
    name = "Dummy Email Service"
    priority = 0
    supports_cc = True
    supports_bcc = True

    def send_email(self, email_message: EmailMessage):
        return True


class MailgunEmailService(EmailService):
    name = "Mailgun"
    supports_cc = True
    supports_bcc = True

    def __init__(self, priority=0):
        self.api_endpoint = "https://api.mailgun.net/v3/{}".format(email_config["email_domain"])
        self.api_key = email_config["api_keys"]["mailgun"]
        self.priority = priority

    def send_email(self, email_message: EmailMessage):

        post_req_payload = {"to": ",".join(email_message.to_recipients),
                            "subject": email_message.subject,
                            "text": "{}\nINFO: Sent via Mailgun Email Service".format(email_message.raw_text_body)
                            }

        if email_message.from_name is not None:
            post_req_payload["from"] = "{} <{}>".format(email_message.from_name, email_message.from_email)
        else:
            post_req_payload["from"] = email_message.from_email

        if len(email_message.to_cc) > 0:
            post_req_payload["cc"] = ",".join(email_message.to_cc)

        if email_message.to_bcc is not None:
            post_req_payload["bcc"] = email_message.to_bcc

        if email_message.html_body is not None:
            post_req_payload["html"] = email_message.html_body

        return requests.post("{}/messages".format(self.api_endpoint), auth=('api', self.api_key), data=post_req_payload)


class SendgridEmailService(EmailService):
    name = "Sendgrid"
    supports_cc = True
    supports_bcc = True

    def __init__(self, priority=0):
        self.sg_context = sendgrid.SendGridAPIClient(apikey=email_config["api_keys"]["sendgrid"])
        self.priority = priority

    def send_email(self, email_message: EmailMessage):
        mail = sendgrid.helpers.mail.Mail()
        personalization = sendgrid.helpers.mail.Personalization()

        if email_message.from_name is not None:
            mail.set_from(sendgrid.helpers.mail.Email(email_message.from_email, email_message.from_name))
        else:
            mail.set_from(sendgrid.helpers.mail.Email(email_message.from_email))

        mail.set_subject(email_message.subject)

        mail.add_content(sendgrid.helpers.mail.Content("text/plain", "{}\nINFO: Sent via Sendgrid Email Service".format(
            email_message.raw_text_body)))

        if email_message.html_body is not None:
            mail.add_content(sendgrid.helpers.mail.Content("text/html", email_message.html_body))

        for t in email_message.to_recipients:
            personalization.add_to(sendgrid.helpers.mail.Email(t))

        for c in email_message.to_cc:
            personalization.add_cc(sendgrid.helpers.mail.Email(c))

        if email_message.to_bcc is not None:
            personalization.add_bcc(sendgrid.helpers.mail.Email(email_message.to_bcc))

        mail.add_personalization(personalization)

        return self.sg_context.client.mail.send.post(request_body=mail.get())
