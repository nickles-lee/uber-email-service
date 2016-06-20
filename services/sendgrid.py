import sendgrid

from email_message import EmailMessage
from services.abstract import AbstractEmailService
from exceptions import *


class SendgridEmailService(AbstractEmailService):
    name = "sendgrid"

    def __init__(self, domain, api_key, priority=0):
        self.api_key = api_key
        self.sg_context = sendgrid.SendGridAPIClient(apikey=api_key)
        self.domain = domain
        self.priority = priority

    def send_email(self, email_message: EmailMessage):
        mail = sendgrid.helpers.mail.Mail()
        personalization = sendgrid.helpers.mail.Personalization()

        if email_message.from_name is not None:
            mail.set_from(sendgrid.helpers.mail.Email(email_message.from_email, email_message.from_name))
        else:
            mail.set_from(sendgrid.helpers.mail.Email(email_message.from_email))

        mail.set_subject(email_message.subject)

        # mail.add_content(sendgrid.helpers.mail.Content("text/plain", "{}\nSent via Sendgrid Email Service".format(
        mail.add_content(sendgrid.helpers.mail.Content("text/plain", "{}".format(
            email_message.raw_text_body)))

        if email_message.html_body is not None:
            mail.add_content(sendgrid.helpers.mail.Content("text/html", email_message.html_body))

        for t in email_message.to_recipients:
            personalization.add_to(sendgrid.helpers.mail.Email(t))

        if email_message.to_cc is not None:
            for c in email_message.to_cc:
                personalization.add_cc(sendgrid.helpers.mail.Email(c))

        if email_message.to_bcc is not None:
            personalization.add_bcc(sendgrid.helpers.mail.Email(email_message.to_bcc))

        mail.add_personalization(personalization)

        resp = self.sg_context.client.mail.send.post(request_body=mail.get())

        # Note that transient (4XX) errors are counted as failures; expedient/guaranteed delivery is ranked higher than
        # ensuring exactly-once sending. This may not be preferable in all contexts
        if resp.status_code in [202, 250]:
            return True
        elif resp.status_code == 421:
            raise RateLimitException(self.name)
        elif resp.status_code in [450, 550, 551, 552, 553]:
            raise RecipientEmailUnavailable(self.name)
        elif resp.status_code in [451, 452, 554]:
            raise GenericEmailRoutingError(self.name)
        else:
            raise GenericEmailRoutingError(self.name)
