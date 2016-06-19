import json
import logging
import sys

from email_message import EmailMessage
from services.abstract import EmailService
from services.mailgun import MailgunEmailService
from services.sendgrid import SendgridEmailService
from exceptions import *


class PooledEmailService(EmailService):
    def __init__(self):
        try:

            email_config = json.loads(open('config.json', 'r').read())
            enabled_domains = {}

            for d in email_config['email_services']:
                services = list()
                for s in d["enabled_services"]:
                    if s == "Mailgun":
                        services.insert(0, MailgunEmailService(d['email_domain'], d['enabled_services'][s]['api_key'],
                                                               d['enabled_services'][s]['priority_value'] if
                                                               d['enabled_services'][s][
                                                                   'priority_value'] is not None else 1))
                    elif s == "Sendgrid":
                        services.insert(0, SendgridEmailService(d['email_domain'], d['enabled_services'][s]['api_key'],
                                                                d['enabled_services'][s]['priority_value'] if
                                                                d['enabled_services'][s][
                                                                    'priority_value'] is not None else 1))

                services.sort(reverse=True, key=(lambda x: x.priority))
                enabled_domains[d['email_domain']] = {"pool_api_key": d['pool_api_key'], "enabled_services": services}

            self.enabled_domains = enabled_domains
            self.root_api_key = email_config.get('root_api_key')

        except:
            logging.error("Fatal error loading pool configurations. (Check JSON syntax?)")
            sys.exit(1)

    def validate_send_email(msg: EmailMessage) -> bool:
        return msg.from_email.split("@").get(1) == email_config.get("email_domain")

    def get_email_services(self, pool_api_key, email_message: EmailMessage):
        domain = email_message.from_email.split("@")[1]
        if domain is not None and domain in self.enabled_domains:
            if pool_api_key == self.enabled_domains[domain]['pool_api_key']:
                return self.enabled_domains[domain]['enabled_services']
            else:
                raise InvalidAPIKeyException
        else:
            raise MismatchedEmailDomainException

    def send_email(self, email_message: EmailMessage, pool_api_key=None):
        services_list = self.get_email_services(pool_api_key, email_message)
        services_unsuccessful = {}

        for s in services_list:
            if s.simulating_failure:
                services_unsuccessful[s.name] = "Simulating Failure"
                continue
            try:
                resp = s.send_email(email_message)
                return {"result": "success",
                        "service_used": s.name,
                        "services_unsuccessful": services_unsuccessful}
            except Exception as e:
                logging.exception(e)
                services_unsuccessful[s.name] = str(e)

        return {"result": "error", "services_unsuccessful": services_unsuccessful}
