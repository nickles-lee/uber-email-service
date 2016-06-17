import time
from abc import ABCMeta, abstractmethod,
from email_message import EmailMessage

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
    def send_email(self, email_message) -> bool : pass

    def set_priority(self, priority_value):
        self.service_priority = priority_value

    def set_service_rate_limit(self, msg_count, seconds):
        self.rate_limit_msg_count = msg_count
        self.rate_limit_window_seconds = seconds
        self.sent_timestamps = filter(lambda x : time.time() - x < seconds)

    # Check if rate limit on service is in effect, clearing timestamp list only if the rate limiter potentially
    # triggers. Has the advantage of having lower amortised time cost, but may result in "lag spikes" if a large
    # rate limit window is hit.
    def check_if_rate_limited(self):
        if self.rate_limit_msg_count < 0:
            return False
        elif len(self.sent_timestamps) < self.rate_limit_msg_count:
            return False
        else:
            self.sent_timestamps = filter(lambda x : time.time() - x < self.rate_limit_window_seconds)
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

    def send_email(self, email_message : EmailMessage) -> bool:
         return True

class MailgunEmailService(EmailService):
    name = "Mailgun"
    priority = 10
    supports_cc