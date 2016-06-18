import email_services
import time
from email_message import EmailMessage

mailgun_service = email_services.MailgunEmailService()
sendgrid_service = email_services.SendgridEmailService()

# test_message = EmailMessage("mailgun@dev.nicklee.de", ["spam0@nickle.es", "spam1@nickle.es"],
#                             "Test Email {}".format(time.time()), "This is a test message.")
#
# mailgun_service.send_email(test_message)
#
# test_message.from_email = "sendgrid@dev.nicklee.de"
#
# sendgrid_service.send_email(test_message)

test_html = EmailMessage("html_test@dev.nicklee.de", "spam@nickle.es", "HTML Enclosed", "This is the raw text view", html_body=open("/Users/nick/Downloads/body.html", "r").read(), from_name="HTML Test")

mailgun_service.send_email(test_html)
sendgrid_service.send_email(test_html)