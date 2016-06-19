import time
from abc import ABCMeta, abstractmethod

from email_message import EmailMessage

class EmailService:
    __metaclass__ = ABCMeta

    name = "Undefined service"
    priority = 0
    simulating_failure = False
    rate_limit_msg_count = -1
    rate_limit_window_seconds = -1
    sent_timestamps = []
    supports_cc = True
    supports_bcc = True

    @abstractmethod
    def send_email(self, email_message: EmailMessage):
        pass

    # def set_service_rate_limit(self, msg_count, seconds):
    #     self.rate_limit_msg_count = msg_count
    #     self.rate_limit_window_seconds = seconds
    #     self.sent_timestamps = filter(lambda x: time.time() - x < seconds, self.sent_timestamps)

    # Check if rate limit on service is in effect, clearing timestamp list only if the rate limiter potentially
    # triggers. Has the advantage of having lower amortised time cost, but may result in "lag spikes" if a large
    # rate limit window is hit.
    # def check_if_rate_limited(self):
    #     if self.rate_limit_msg_count < 0:
    #         return False
    #     elif len(self.sent_timestamps) < self.rate_limit_msg_count:
    #         return False
    #     else:
    #         self.sent_timestamps = filter(lambda x: time.time() - x < self.rate_limit_window_seconds,
    #                                       self.sent_timestamps)
    #         if len(self.sent_timestamps) < self.rate_limit_msg_count:
    #             return False
    #         else:
    #             return True

    def toggle_failure_mode(self):
        self.simulating_failure = not self.simulating_failure
        return {"service_name": self.name, "simulated_failure_enabled": self.simulating_failure}