class IPKException(Exception):
    pass

class IncorrectHTTPMethodException(IPKException):
    def __init__(self, usedMethod, expectedMethod):
        IPKException.__init__(self, f'Used method {usedMethod}, expected method {expectedMethod}')

class IncorrectGETFormatException(IPKException):
    pass

class IncorrectURLRequestException(IPKException):
    def __init__(self, usedRequest, expectedRequest):
        IPKException.__init__(self, f'Used request {usedRequest}, expected request {expectedRequest}')

class IncorrectDNSTypeException(IPKException):
    '''Raised when the type is not 'A' or 'PTR' '''
    def __init__(self, usedType, expectedType):
        IPKException.__init__(self, f'Got type {usedType}, expected type {expectedType}')