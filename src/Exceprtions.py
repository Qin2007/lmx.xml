pass


class BaseXMLException(Exception):
    pass


class XKeyExrror(BaseXMLException, KeyError):
    pass


class XMLNotImplementedError(BaseXMLException):
    pass


class XMLEqualsWarning(BaseXMLException):
    pass


pass
