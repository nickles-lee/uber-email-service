import sys, getopt

import requests

url = ""
domain = ""
dest_email = ""
pool_api_key = ""
root_api_key = ""

try:
    url = sys.argv[1]
    domain = sys.argv[2]
    dest_email = sys.argv[3]
    pool_api_key = sys.argv[4]
    root_api_key = sys.argv[5]
except IndexError:
    print(
        "Usage: 'python3 integrationtest_online.py [base_api_url] [domain] [destination_email] [pool_api_key] [root_api_key]")
    sys.exit(1)

full_text_query = requests.post("{}/{}/send".format(url, domain), headers={"Accept": "application/json"}, json={
    'pool_api_key': pool_api_key,
    'from_email': "test@{}".format(domain),
    "to_recipients": [dest_email],
    "to_cc": dest_email,
    "to_bcc": dest_email,
    "subject": "1: Test Subject",
    "raw_text_body": "Sent via top priority service sendgrid"
})

bad_bcc = requests.post("{}/{}/send".format(url, domain), headers={"Accept": "application/json"}, json={
    'pool_api_key': pool_api_key,
    'from_email': "test@{}".format(domain),
    "to_recipients": dest_email,
    "to_bcc": ["foo@example.com", "bademail.com"],
    "subject": "2: Bad BCC",
    "raw_text_body": "Sent via top priority service sendgrid"
})

html_test = requests.post("{}/{}/send".format(url, domain), headers={"Accept": "application/json"}, json={
    'pool_api_key': pool_api_key,
    'from_email': "test@{}".format(domain),
    "to_recipients": dest_email,
    "subject": "3: Testing HTML",
    "raw_text_body": "This is an HTML Email.",
    "html_body": "<h1>Hello World</h1><p>Hello sendgrid</p>"
})

toggle_sendgrid = requests.post("{}/{}/sendgrid/fail".format(url, domain), headers={"Accept": "application/json"},
                                json={"root_api_key": root_api_key})

mg_ftq = requests.post("{}/{}/send".format(url, domain), headers={"Accept": "application/json"}, json={
    'pool_api_key': pool_api_key,
    'from_email': "test@{}".format(domain),
    "to_recipients": [dest_email],
    "to_cc": dest_email,
    "to_bcc": dest_email,
    "subject": "4: Mailgun Email",
    "raw_text_body": "Sent via low priority service mailgun"
})

mg_bbcc = requests.post("{}/{}/send".format(url, domain), headers={"Accept": "application/json"}, json={
    'pool_api_key': pool_api_key,
    'from_email': "test@{}".format(domain),
    "to_recipients": dest_email,
    "to_bcc": ["foo@example.com", "bademail.com"],
    "subject": "5: I shouldn't see this",
    "raw_text_body": "Sent via low priority service mailgun"
})

mg_html = requests.post("{}/{}/send".format(url, domain), headers={"Accept": "application/json"}, json={
    'pool_api_key': pool_api_key,
    'from_email': "test@{}".format(domain),
    "to_recipients": dest_email,
    "subject": "6: Mailgun HTML",
    "raw_text_body": "This is an HTML Email.",
    "html_body": "<h1>Hello World</h1><p>Hello mailgun</p>"
})

toggle_mg = requests.post("{}/{}/mailgun/fail".format(url, domain), headers={"Accept": "application/json"},
                          data={"root_api_key": root_api_key})

this_will_fail = requests.post("{}/{}/send".format(url, domain), headers={"Accept": "application/json"}, json={
    'pool_api_key': pool_api_key,
    'from_email': "test@{}".format(domain),
    "to_recipients": [dest_email],
    "to_cc": dest_email,
    "to_bcc": dest_email,
    "subject": "7: This will fail",
    "raw_text_body": "This is being sent through nothing because both services are down"
})

# Re-Enable both services
cleanup = requests.post("{}/{}/mailgun/fail".format(url, domain), headers={"Accept": "application/json"},
                          data={"root_api_key": root_api_key})
cleanup_2 = requests.post("{}/{}/sendgrid/fail".format(url, domain), headers={"Accept": "application/json"},
                                json={"root_api_key": root_api_key})

print("Messages will return false if response code is not what is expected.")
print("Bog-Standard Email:\t", full_text_query.status_code == 200)
print("Bad BCC Email:\t", bad_bcc.status_code == 500)
print("HTML Email:\t", html_test.status_code == 200)
print("Simulating failure on Sendgrid\t", toggle_sendgrid.status_code == 200)
print("Bog-Standard Email:\t", mg_ftq.status_code == 200)
print("Bad BCC Email:\t", mg_bbcc.status_code == 500)
print("HTML Email:\t", mg_html.status_code == 200)
print("Simulating failure on Mailgun\t", toggle_mg.status_code == 200)
print("Failed email\t", this_will_fail.status_code == 503)



