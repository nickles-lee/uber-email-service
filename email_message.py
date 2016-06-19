import ujson


# Enforces the inclusion of a subject and message body. If a single recipient is provided, it is cast to a list
# This class is used in place of MIMEMultipart because
class EmailMessage:
    def __init__(self, from_email, to_recipients, subject, raw_text_body,
                 to_cc=list(), to_bcc=None, html_body=None, from_name=None):

        self.from_email = from_email
        self.subject = subject
        self.raw_text_body = raw_text_body
        if type(to_recipients) is not list:
            if type(to_recipients) is str:
                self.to_recipients = [to_recipients]
            else:
                raise TypeError
        else:
            self.to_recipients = to_recipients

        if to_cc is None:
            self.to_cc = None
        elif type(to_cc) is str:
            self.to_cc = [to_cc]
        elif type(to_cc) is list:
            self.to_cc = to_cc
        else:
            raise TypeError

        if to_bcc is None:
            self.to_bcc = None
        elif type(to_bcc) is not str:
            raise TypeError
        else:
            self.to_bcc = to_bcc

        if html_body is None:
            self.html_body = None
        else:
            self.html_body = html_body

        if from_name is None:
            self.from_name = None
        else:
            self.from_name = from_name

    def __str__(self):
        out = {
            "Sender": self.from_email,
            "Recipients": self.to_recipients,
            "Subject": self.subject
        }
        return ujson.dumps(out)
