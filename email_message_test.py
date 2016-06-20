import pytest
from email_message import EmailMessage


# test_html = EmailMessage("html_test@dev.nicklee.de", "spam@nickle.es", "HTML Enclosed", "This is the raw text view", html_body=open("/Users/nick/Downloads/body.html", "r").read(), from_name="HTML Test")
#
#
#
def test_from_email_validate():
    with pytest.raises(TypeError):
        foo = EmailMessage("bad_email_no_at", "single_destination@example.com", "subject", "raw_text_body")


def test_single_to():
    assert isinstance(EmailMessage("test@example.com", "single_destination@example.com", "subject", "raw_text_body"),
                      EmailMessage)


def test_multiple_to():
    assert isinstance(EmailMessage("test@example.com", ["1@example.com", "2@example.com"], "subject", "raw_text_body"),
                      EmailMessage)


def test_invalid_to():
    with pytest.raises(TypeError):
        EmailMessage("test@example.com", 123, "subject", "raw_text_body")


# Tests for CC, BCC should go here

def test_multiple_bcc():
    with pytest.raises(TypeError):
        EmailMessage("test@example.com", "1@example.com", "subject", "raw_text_body",
                     to_bcc=["1@example.com", "2@example.com"])

# Toss in some tests for unicode & such