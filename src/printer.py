import datetime
import json
import types

pass


class Printer:
    def __init__(self, openf, printconsole=False):
        self.printconsole = printconsole
        self.openf = openf
        self.total = 0

    def out(self, strx: str, printconsole=None):
        self.openf.write(strx)
        self.total += len(strx.encode())
        if (
                (self.printconsole and printconsole) and printconsole is not False
        ):
            print(strx, sep='', end='')
        return self

    def return_(self):
        def cbyte(num):
            for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
                if num < 1024.0:
                    break
                num = num / 1024.0
            return f'{num:.1f} {x}'

        return cbyte(self.total)

    pass


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return obj.to_json()
        except AttributeError:

            if isinstance(obj, types.GeneratorType):
                return [i for i in obj]
            try:
                return super().default(obj)
            except TypeError:
                return 'python:' + repr(obj)
        pass

    pass


def jdumper(jkson, indent=None):
    return json.dumps(jkson, cls=CustomEncoder, indent=indent)


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc)


def httpdate(dt):
    """Return a string representation of a date according to RFC 1123 (HTTP/1.1).
    The supplied date must be in UTC."""
    weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()]
    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][dt.month - 1]
    return f"{weekday}, {dt.day} {month} {dt.year} {dt.hour:02d}:{dt.minute:02d}:{dt.second:02d} GMT"


pass
