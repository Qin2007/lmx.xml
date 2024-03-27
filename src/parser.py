import re

import bs4
from bs4 import BeautifulSoup
import json

from src.printer import Printer


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            return repr(obj)

    pass


def jdumper(jkson, indent=None):
    return json.dumps(jkson, cls=CustomEncoder, indent=indent)


class XScripter:
    def __init__(self, script):
        self._xfunctions = dict()
        self.__script = script
        self.conf = {
            'out.txt': 'out.txt',
            'dump.json': 'dump.json',
            'dump.txt': 'dump.txt'}
        self.__parsedata = None
        self.__xmlns = "https://ant.ractoc.com/xmlns/lmx/0/0/0/index.doctype"
        self._ismain = False

    @property
    def scriptf(self):
        return re.sub('<!--.*-->', '', f'{self.__script}', flags=re.DOTALL)

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
            obj['children'] = [i for i in obj['children'] if i is not None and i != '\n']
            return obj

        return xml_element_to_obj(soup.find())

    def _exec(self, exl, printer, vardict):
        match (exl['ElementName']):
            case 'xout':
                self._xout(exl, 'xml', printer)
            case 'xecho':
                self._xout(f"{vardict[exl['attrs']['var']]}", 'str', printer)
            case 'xcall':
                self._callfunc(exl['attrs']['xname'], printer)
            case 'xfor':
                for var in range(int(exl['attrs']['start']), int(exl['attrs']['stop']), int(exl['attrs']['step'])):
                    vardict[exl['attrs']['var']] = var
                    for exlc in exl['children']:
                        self._exec(exlc, printer, vardict)
            case 'xfunction':
                return
        return

    def _callfunc(self, xfunction, printer):
        xgfunction = self._xfunctions[xfunction]
        xgfunction['vardict'] = dict()
        for exl in xgfunction['children']:
            self._exec(exl, printer, xgfunction['vardict'])
        return

    def _xmlstart(self, exl, printer, toplvl):
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
                self._xout(exl, 'xml', printer)
        pass

    def _xout(self, lixt, type_, printer):
        (lambda _: _)(self)
        # return ' '.join((i if isinstance(i, str) else (self._xout(i['xml']))) for i in lixt) + '\n'
        match type_:
            case 'xml':
                printer.out(lixt['xml'])
            case 'str':
                printer.out(lixt)

        return ''

    def xmlrun(self):
        with (open(self.conf['out.txt'], 'wt', encoding='utf-8') as outfile,
              open(self.conf['dump.json'], 'wt', encoding='utf-8') as jdump):
            printer, jdump = Printer(outfile), Printer(jdump)
            try:
                self._xmlstart(self.__parsedata, printer=printer, toplvl=True)
                if self._ismain:
                    self._callfunc('main', printer)
            finally:
                jdump.out(jdumper({'xml': self.__parsedata, 'xfuncs': self._xfunctions}, indent=4))
                print('out', printer.return_())
                print('jdump', jdump.return_())
        return self

    def xmlparse(self):
        self.__parsedata = self._xmlparse_ai(self.scriptf)
        return self

    @classmethod
    def file_get_contents(cls, openxml):
        with open(openxml, 'rt', encoding='utf-8') as xml:
            return cls(xml.read())
        pass

    def setconf(self, key, val):
        self.conf[key] = val
        return self

    pass


if __name__ == '__main__':
    (XScripter.file_get_contents('./testfile.xml')
     .setconf('out.txt', 'out1.txt')
     .setconf('dump.json', 'dump1.json')
     .setconf('dump.txt', 'dump1.txt')
     .xmlparse().xmlrun())
    (XScripter.file_get_contents('./secondtest.xml')
     .setconf('out.txt', 'out2.txt')
     .setconf('dump.json', 'dump2.json')
     .setconf('dump.txt', 'dump2.txt')
     .xmlparse().xmlrun())
    pass
pass
