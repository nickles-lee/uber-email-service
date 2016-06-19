class RateLimitException(Exception):
    def __init__(self, limited_service):
        self.limited_service = limited_service

    def __str__(self):
        return "Rate Limit on {} hit".format(self.limited_service)


class InvalidAPIKeyException(Exception):
    def __init__(self, service):
        self.service = service

    def __str__(self):
        return "API Key Error on {} ".format(self.service)


class MissingAPIKeyException(Exception):
    def __init__(self, service):
        self.service = service

    def __str__(self):
        return "No API Key for {} ".format(self.service)


class MismatchedEmailDomainException(Exception):
    def __init__(self, domain):
        self.service = domain

    def __str__(self):
        return "Mismatched domain specified: {} ".format(self.service)

class RecipientEmailUnavailable(Exception):
    def __init__(self, service):
        self.service = service

    def __str__(self):
        return "Recipient does not exist or is blocked on {} ".format(self.service)

class GenericEmailRoutingError(Exception):
    def __init__(self, service):
        self.service = service

    def __str__(self):
        return "An email routing error occurred at the service {} ".format(self.service)