try:
    UNICODE_EXISTS = bool(type(unicode))
except NameError:
    unicode = str
