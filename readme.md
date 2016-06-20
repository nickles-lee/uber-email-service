# Nick Lee's Uber Coding Challenge

## Project: Email Service, Backend Track

Many web and server services need to send large quantities of email. Due to the complexities of ensuring mail delivery, and avoiding spam blacklists, it is common to use an email service provider optimised for sending messages from an API.

This service is designed to provide a high-level abstraction that reduces the complexity of using multiple email providers. It provides seamless failover between multiple providers on multiple email domains, and its code design facilitates the modular addition of new services.

##Architecture:
The service is implemented in the form of a browsable Python-Flask API; the 'accept' header in the request determines whether to serve a browsable page with documentation or whether to serve raw JSON.

The email service pooling is built off of three main components:

* AbstractEmailService and children: All email services are children of a  common class, which allows them to be tracked in one data structure.
* config.json: Available/enabled services, their priorities, and their API keys are all defined via a single JSON file passed to the server at startup. This allows for multiple users from different email domains to share a single Flask server without sharing API keys. Assuming that the security risk was ruled acceptable, this mapping could be uploaded/updated by someone with appropriate credentials in order to avoid the need to touch any server-side config files.

     The schema may be found in config_example.json
* uber-email-service: This is the Flask endpoint that verifies that API calls have appropriate permissions and performs appropriate serialisation/deserialisation.

##Security:
The deployment in Heroku uses TLS to protect data in transit. API keys are excluded from version control in order to prevent automated harvesting, and two levels of API access exist. The Python Requests library and Flask provide basic input sanitization

Level one provides access to the pooling service for a particular domain, while level two provides access to the API keys for each domain and the ability to enable/disable a simulated failure mode for each service.

In a production environment, the ability to list API keys or domains would not be enabled; it serves more as a proof of concept for the existence of an administrative API key. The ability to upload new configurations *could* be added depending on user needs, but it would greatly increase the power and risk associated with the root\_api\_key.

Rate limiting is not implemented due to a lack of clarity about the point at which Sendgrid/Mailgun rate limit queries. In case of abuse, rate-limiting would occur outside of the service.

##Testing:
Two test apparatuses are available.

The first test apparatus (pytest) provides unit testing of the Python modules and functions. It may be triggered with py.test

The second test apparatus provides an integration test. Simply specify the destination email address, and it will send a series of emails with different parameters. Manual verification of those emails is required, although an automated testing system could monitor an email inbox and check the incoming emails against the expected results.

    python3 integrationtest_online.py 'https://whispering-taiga-53034.herokuapp.com' $DOMAIN $RECIPIENT_EMAIL $POOL_API_KEY $ROOT_API_KEY

##UX:
The user interface consists of a boilerplate Flask-API, plus documentation. The following API endpoints exist:

* / : List available domains and their services/priorities.

* /[domain] : List domain and its services/priorities.

* /[domain]/[provider]/fail : Toggle simulated failure on a domain's service.

* /[domain]/send : Send an email through the pooled service.

* /[domain]/[provider]/send: This endpoint is not implemented, but if the ability to bypass the pooled email service was desired, it would be quick to make it possible to explicitly specify a particular email provider to send with.


##Libaries:

* Python abstract base classes
* Flask: Used to provide a web API
* Flask-API: Used to provide a boilerplate browsable-API frontend
* Markdown: Used to embed documentation within Flask-API frontends.
* Python Requests: Used to make requests to Mailgun, as they only provide an HTTP API
* Python sendgrid: Sendgrid's native Python module is used on the assumption that they have optimised its performance.
* Python's Email/MIME classes are _not_ used due to the need to make requests using different email representations. Using standardised classes is generally preferable to creating a new one. The Python MIME classes' manner of representing multiple email recipients is cumbersome for this project.

##Scalability:
This application can be scaled upwards in a variety of ways:

* Requests could be naively load-balanced in a round-robin manner.

* Requests could be load-balanced by domain, with low-activity domains being grouped on one process while high-activity domains run in separate processes. This distribution would be handled through a load balancer, which would still allow for failover if a particular process dies.
* The Flask endpoint could be modified to accept multiple messages at once. If an email service supports batched messages, those messages would be batched all at once to reduce network overhead, with sequential/individual sending used as a fallback for providers that don't support batching/bulk email.

* The Flask endpoint could be decoupled from the email-sending code. Once validated and accepted, email messages would be inserted into a Kafka topic to be sent as soon as possible. This has the advantage of being able to better tolerates bursts of activity while having the (arguable) disadvantage of making email processing asynchronous. This would have better fault tolerance and optimisability than a service that only does local batching of emails before sending.

##Production Readiness:
###Monitoring:
No monitoring is included in this deployment.  This could be quickly implemented in one of two ways:

1. Have a load balancer/heartbeat checker periodically query one of the API endpoints and raise an alarm if the request fails.
2. Have the application or monitoring service periodically send emails, and raise an alarm if the emails do not arrive in a timely manner. This would be preferable if we are concerned with email deliverability, and not just API availability.

###Logging
Logging is handled by the Python logger class. Logging parameters are specified at runtime, or in this case the Heroku Procfile.
The extent of logging could be improved. In practice, activity on API endpoints, exceptions, and authorisation failures should be logged.

In a minimum production instance, Logrotate would be used to prevent logs from becoming excessively large.

For security, a centralised write-only logging system could be used. I personally like using an Eastic-Logstash-Kibana stack.

###Error Handling:
Error checking occurs with function inputs, when classes/data structures are instantiated, and at API endpoints.

Exceptions for a variety of failure conditions exist, and are used to standardise the handling of different email service errors.

It should not be possible to compromise the state of the server via bad inputs; most exceptions are caught before they can cause harm, returning an internal server error at worst.

###Deployment:
The service is deployed to Heroku. In order to avoid inclusion of API keys in the version control, the config.json file is
exclusively committed to the heroku deployment branch, which is not on Github.

In a full-production environment, the config file would be served from Amazon S3 as described in the documentation:
https://devcenter.heroku.com/articles/s3

###Git-flow:
The git repository features a single branch because it only had one developer and was in a very early stage.
From the first "release" onwards, or if there is more than one developer, I like using feature-branching.
(One branch per card)

#Links:
* Hosted Application: https://whispering-taiga-53034.herokuapp.com/
* GitHub Repository: https://github.com/nickles-lee/uber-email-service
* June 2016 CV: https://github.com/nickles-lee/uber-email-service/blob/master/cv_Nick%20Lee.pdf
* Service Config file: Not hosted online, to be shared with recruiting by email. (I'm assuming you also make your own)
