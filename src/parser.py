import pathlib
import re
import datetime

import bs4
from bs4 import BeautifulSoup
import json

from src.printer import Printer


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, XScripter):
            return obj.to_json()
        try:
            return super().default(obj)
        except TypeError:
            return 'python:' + repr(obj)

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


class XScripter:
    def __init__(self, script):
        self._xfunctions = dict()
        self.__script = script
        self.conf = {
            'out.txt': 'out.txt',
            'dump.json': 'dump.json',
            'cwd': pathlib.Path.cwd()}
        self.__parsedata = None
        self.__xmlns = "https://ant.ractoc.com/xmlns/lmx/0/0/0/index.php"
        self._ismain = False
        self.__modules = dict()

    @property
    def scriptf(self):
        return re.sub('<!--.*-->', '', f'{self.__script}', flags=re.DOTALL)

    def to_json(self):
        return {'xml': self.__parsedata, 'xfuncs': self._xfunctions}

    @property
    def xmlns(self):
        return self.__xmlns

    @staticmethod
    def _xmlparse_ai(markup):
        soup = BeautifulSoup(markup, 'xml')

        def xml_element_to_obj(element):
            if isinstance(element, bs4.element.NavigableString):
                return str(element)
            if element is None:
                return None
            obj = {'ElementName': element.name, 'xmlns': element.namespace,
                   'children': [xml_element_to_obj(child) for child in element.children],
                   'attrs': {attr: value for attr, value in element.attrs.items()},
                   'striped': [i for i in element.stripped_strings],
                   'strings': [i for i in element.strings], 'xml': repr(element)}
            obj['children'] = [i for i in obj['children'] if i is not None and not (i == '\n' or i == ' ')]
            return obj

        return xml_element_to_obj(soup.find())

    def _exec(self, exl, printer, vardict, xfunction):
        match (xmlname := exl['ElementName']):
            case 'xout':
                self._xout(exl['children'], 'lix', printer)
            case 'xecho':
                value = vardict[exl['attrs']['var']]
                if isinstance(value, datetime.datetime):
                    self._xout(httpdate(value), 'str', printer)
                else:
                    self._xout(f"{value}", 'str', printer)
            case 'xcall':
                returnto = self._callfunc(exl['attrs']['xname'], printer)
                if returnto is not None:
                    vardict[exl['attrs']['returnto']] = returnto
            case 'xfor':
                for var in range(int(exl['attrs']['start']), int(exl['attrs']['stop']), int(exl['attrs']['step'])):
                    vardict[exl['attrs']['var']] = var
                    for exlc in exl['children']:
                        self._exec(exlc, printer, vardict, xfunction)
            case 'xfunction':
                return
            case 'new':
                # set_as = None
                match (exl['attrs']['type']):
                    case 'datetime':
                        set_as = utcnow()
                    case 'String':
                        set_as = exl['attrs']['value']
                    case 'Array':
                        set_as = [i for i in exl['children'] if (i['ElementName'] == 'li' and i['xmlns'] == self.xmlns)]
                    case _:
                        raise ValueError('unsupported type ' + f"{exl['attrs']['type']}")
                if set_as is not None:
                    vardict[exl['attrs']['setas']] = set_as
            case 'return':
                return vardict[exl['attrs']['var']]
            case 'desc':
                return
            case 'include':
                module = self.__modules[(importas := exl['attrs']['as'])] = \
                    XScripter.file_get_contents(
                        self.conf['cwd'] / exl['attrs']['src']
                    ).xmlparse().xmlrun(suppress=True)._xfunctions
                for xname, xfunc in module.items():
                    if xname == 'main':
                        continue
                    if self._xfunctions.get(f'{importas}.{xname}') is not None:
                        raise ValueError(f'{importas}.{xname} exxists already')
                    self._xfunctions[f"{importas}.{xname}"] = xfunc
                pass
            case _:
                print(xmlname, 'is not a supported element, if this is intentional ',
                      'please add it to an xignel element to suppress this warning')
                pass  # X IGN ore Element
        return None

    def _callfunc(self, xfunction, printer):
        xgfunction = self._xfunctions[xfunction]
        xgfunction['vardict'] = dict()
        for exl in xgfunction['children']:
            returnto = self._exec(exl, printer, xgfunction['vardict'], xgfunction)
            if returnto is not None:
                return returnto
        return None

    def _xmlstart(self, exl, printer, toplvl):
        if exl is None:
            return
        if exl['ElementName'] == 'xfunction' and exl['xmlns'] == self.__xmlns:
            funcname = exl['attrs']['xname']
            if self._xfunctions.get(funcname) is not None:
                raise ValueError(f'{funcname} exxists already')
            self._xfunctions[funcname] = exl
            if funcname == 'main':
                self._ismain = True
            for child in exl['children']:
                self._xmlstart(child, printer, False)
        else:
            if toplvl:
                raise ValueError('the frst element must be an xfunction of our xmlns')
        pass

    @staticmethod
    def _xout(lixt, type_, printer, end='\n', split=''):
        rtrn = ''
        match type_:
            case 'xml':
                rtrn = lixt['xml']
            case 'lix':
                rtrn = split.join(lixt)
            case 'str':
                rtrn = lixt
        printer.out(rtrn := (rtrn + end))
        return rtrn

    def xmlrun(self, *, return_=False, suppress=False):
        started_at = utcnow()
        with (open(self.conf['out.txt'], 'wt', encoding='utf-8') as outfile,
              open(self.conf['dump.json'], 'wt', encoding='utf-8') as jdump):
            printer, jdump = Printer(outfile), Printer(jdump)
            printer.out(httpdate(started_at)).out('\n').out('\n')
            try:
                self._xmlstart(self.__parsedata, printer=printer, toplvl=True)
                if self._ismain:
                    self._callfunc('main', printer)
            finally:
                jdump.out(jdumper(self.to_json(), indent=4))
                out_ = printer.return_()
                jdump_ = jdump.return_()
                if not suppress:
                    print('out', out_)
                    print('jdump', jdump_)
                if return_:
                    return out_, jdump_
        return self

    def xmlparse(self):
        self.__parsedata = self._xmlparse_ai(self.scriptf)
        return self

    @classmethod
    def file_get_contents(cls, openxml):
        n_ext = (xpath := pathlib.Path(openxml)).stem
        xpath = xpath.parent
        (opath := xpath / 'xout').mkdir(exist_ok=True)
        with open(openxml, 'rt', encoding='utf-8') as xml:
            clss = (cls(xml.read())
                    .setconf('out.txt', f'{opath}/{n_ext}-out.txt')
                    .setconf('dump.json', f'{opath}/{n_ext}-dump.json')
                    .setconf('cwd', xpath))
            return clss
        pass

    def setconf(self, key, val):
        self.conf[key] = val
        return self

    pass


if __name__ == '__main__':
    XScripter.file_get_contents('./xsrc/testfile.xml').xmlparse().xmlrun()
    pass
pass
