from flask import request
from flask.ext.api import FlaskAPI, status

from services.mailgun import MailgunEmailService
from services.pool import PooledEmailService
from services.sendgrid import SendgridEmailService
from email_message import EmailMessage

app = FlaskAPI(__name__)
pool = PooledEmailService()


def domain_repr(domain, is_root_admin=False, list_endpoint_urls=False):
    dom = pool.enabled_domains.get(domain)
    if dom is None:
        return None

    out = {"domain": domain, "url": request.host_url + domain}
    if is_root_admin and list_endpoint_urls:
        out["services"] = list(map(lambda x: {
            "name": x.name,
            "priority": x.priority,
            "api_key": x.api_key,
            "url_toggle_failure": "{}{}/{}/fail".format(request.host_url, domain, x.name)
        }, dom['enabled_services']))
    elif is_root_admin:
        out["services"] = list(
            map(lambda x: {"name": x.name, "priority": x.priority, "api_key": x.api_key}, dom['enabled_services']))
    else:
        out["services"] = list(map(lambda x: {"name": x.name, "priority": x.priority}, dom['enabled_services']))

    if list_endpoint_urls:
        #     out["toggle_provider_failure"]
        out["url_send_email"] = "{}{}/send".format(request.host_url, domain)

    return out


@app.route('/', methods=['GET', 'POST'])
def list_domains():
    """
    List domains registered with email pooling service.
    POST with admin credentials to view further information.
    """
    if request.method == 'POST' and request.data.get('root_api_key') == pool.root_api_key:
        return [domain_repr(dom, is_root_admin=True) for dom in pool.enabled_domains]
    else:
        return [domain_repr(dom) for dom in pool.enabled_domains]


@app.route('/<domain>/', methods=['GET', 'POST'])
def list_domain_providers(domain):
    """
    List a single domain registered with email pooling service, with URLs to relevant endpoints.
    POST with admin credentials to view further information.
    """

    if pool.enabled_domains.get(domain) is None:
        return {"error": "requested domain not found"}, status.HTTP_404_NOT_FOUND
    elif request.method == 'POST' and request.data.get('root_api_key') == pool.root_api_key:
        return [domain_repr(dom, is_root_admin=True, list_endpoint_urls=True) for dom in pool.enabled_domains]
    else:
        return [domain_repr(dom, list_endpoint_urls=True) for dom in pool.enabled_domains]


@app.route('/<domain>/send', methods=['GET', 'POST'])
def send_pooled_email(domain):
    """
    Send an email via pooled email services available on the specified domain.

    Parameters:

    * 'pool_api_key' (required): API Key used to access the pooled services on the domain
    * 'from_email' (required): Email to send message from. Email must belong to the specified domain.
    * 'to_recipients' (required): Either a single email address or a list of addresses to send to
    * 'to_cc' (optional): Either a single email address or a list of addresses to send to
    * 'to_bcc' (optional): a string containing a recipient email address. (Multiple BCCs are not supported by some providers)
    * 'subject' (required): Subject line for email
    * 'raw_text_body' (required): Raw text body for email. Generally replaced by HTML in clients if available
    * 'html_body' (optional): HTML body for email. Requires client support to view properly.

    """
    if request.method == 'GET':
        return {"error": "this call only accepts POST requests"}, status.HTTP_400_BAD_REQUEST
    elif pool.enabled_domains.get(domain) is None:
        return {"error": "requested domain is not found"}, status.HTTP_404_NOT_FOUND
    elif request.method == 'POST' and request.data.get('pool_api_key') == pool.enabled_domains[domain]['pool_api_key']:
        try:
            from_email = request.data['from_email']
            from_name = request.data.get('from_name')

            to_recipients = request.data['to_recipients']
            to_cc = request.data.get('to_cc')
            to_bcc = request.data.get('to_bcc')

            subject = request.data['subject']

            raw_text_body = request.data['raw_text_body']
            html_body = request.data.get('html_body')
        except KeyError:
            return {"error": "missing mandatory parameter"}, status.HTTP_400_BAD_REQUEST
        except TypeError:
            return {"error": "invalid parameter provided"}, status.HTTP_400_BAD_REQUEST


        return pool.send_email(
            EmailMessage(from_email, to_recipients, subject, raw_text_body,
                         to_cc=to_cc, to_bcc=to_bcc, html_body=html_body, from_name=from_name))
    else:
        return {"error": "valid pool api key required for sending emails"}, status.HTTP_401_UNAUTHORIZED


@app.route('/<domain>/<provider>/fail', methods=['GET', 'POST'])
def toggle_simulated_failure(domain, provider):
    """
    Toggle simulated failure mode for a given provider on a given domain.
    Requires admin credentials to be provided
    """

    if pool.enabled_domains.get(domain) is None:
        return {"error": "requested domain is not found"}, status.HTTP_404_NOT_FOUND
    elif request.method == 'POST' and request.data.get('root_api_key') == pool.root_api_key:
        if provider == "mailgun":
            for s in pool.enabled_domains[domain]['enabled_services']:
                if isinstance(s, MailgunEmailService):
                    return s.toggle_failure_mode()
        elif provider == "sendgrid":
            for s in pool.enabled_domains[domain]['enabled_services']:
                if isinstance(s, SendgridEmailService):
                    return s.toggle_failure_mode()
        return {"error": "requested service is not found"}, status.HTTP_404_NOT_FOUND

    else:
        return {"error": "root api key required for failure simulation"}, status.HTTP_401_UNAUTHORIZED


if __name__ == '__main__':
    app.run()
