import ujson


# Enforces the inclusion of a subject and message body. If a single recipient is provided, it is cast to a list
# This class is used in place of MIMEMultipart because
class EmailMessage:
    def __init__(self, from_email, to_recipients, subject, raw_text_body,
                 to_cc=list(), to_bcc=None, html_body=None, from_name=None):

        self.from_email = from_email
        if type(to_recipients) is not list:
            if type(to_recipients) is str:
                self.to_recipients = [to_recipients]
            else:
                raise TypeError
        else:
            self.to_recipients = to_recipients

        self.subject = subject
        self.raw_text_body = raw_text_body

        if to_cc is not None and type(to_cc) is not list:
            if type(to_cc) is str:
                self.to_cc = [to_cc]
            else:
                raise TypeError
        else:
            self.to_cc = to_cc

        if to_bcc is not None and type(to_bcc) is not str:
            raise TypeError
        elif to_bcc is not None:
            self.to_bcc = to_bcc
        else:
            self.to_bcc = None

        self.html_body = html_body
        self.from_name = from_name

    def __str__(self):
        out = {
            "Sender": self.from_email,
            "Recipients": self.to_recipients,
            "Subject": self.subject
        }
        return ujson.dumps(out)
