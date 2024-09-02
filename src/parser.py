import pathlib
import re
import datetime
import tempfile
import time
import types
from pprint import pprint

import toml
import bs4
from bs4 import BeautifulSoup

from src.printer import Printer
from Exceprtions import *


class XScripter:
    def __init__(self, script, docsfile='help.toml'):
        self._xfunctions = dict()
        self.__script = script
        self.conf = {
            'out.txt': 'out.txt',
            'dump.json': 'dump.json',
            'cwd': pathlib.Path.cwd(),
            '__name': '__undef__',
            'printconsole': True}
        self.__parsedata = None
        self.__xmlns = "https://ant.ractoc.com/xmlns/lmx/0/0/0/index.php"
        self._ismain = False
        self.__modules = dict()
        with open(docsfile, 'rt', encoding='utf-8') as tomlfile:
            self.__helpstmt = toml.loads(tomlfile.read())['help']
        self.___undef = '__undef'
        self.__undef = dict(value=[self.___undef], type=self.___undef)
        self.__openfor_run = True

    @property
    def scriptf(self):
        return re.sub('<!--.*-->', '', f'{self.__script}', flags=re.DOTALL)

    def to_json(self):
        return {'xml': self.__parsedata, 'xfuncs': self._xfunctions}

    def _edit_vardict(self, name, value, type_, vardict):
        match type_:
            case 'datetime':
                value_as = utcnow()
            case 'String':
                value_as = value
            case 'char':
                value_as = value[0]
            case 'Array':
                set_as = list()

                for i in value:
                    if i['type'] == 'xml':
                        i['attrs']['setas'] = 'xmlns8923'
                        self._createnew(i, dix := dict())
                        set_as.append(dix['xmlns8923'])
                    else:
                        set_as.append(i)
                value_as = set_as
            case 'Object':
                value_as = value
            case _:
                raise ValueError('unsupported type ' + f"{type_}")
        if value_as is not None:
            vardict[name] = dict(value=value_as, type=type_)
        return self

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
                   'striped': [i for i in element.stripped_strings], 'type': 'xml',
                   'strings': [i for i in element.strings], 'xml': repr(element)}
            obj['children'] = [i for i in obj['children'] if i is not None and not (i == '\n' or i == ' ')]
            return obj

        return xml_element_to_obj(soup.find())

    def _createnew(self, exl, vardict):
        self._edit_vardict(
            exl['attrs']['setas'],
            exl['strings'] if exl['attrs']['type'] == 'String' else exl['children'],
            exl['attrs']['type'],
            vardict)
        return

    @staticmethod
    def _to_string_from_object(object_, type_=None):
        return (
            ''.join(object_) if type_ == 'String' else object_
        ) if type_ is not None else (
            ''.join(object_['value']) if object_['type'] == 'String'
            else object_['value'])
        pass

    def _to_string(self, property_: dict, fromself=False):
        value = property_['value']
        with tempfile.TemporaryFile() as tempofile:
            match property_['type']:
                case 'String':
                    tempofile.write(''.join(value).encode(encoding='utf-8'))
                case 'Array':
                    property__ = (self._to_string(i, True) for i in value)
                    if fromself:
                        return property__
                    tempofile.write(jdumper(property__, indent=2).encode(encoding='utf-8'))
                case 'char':
                    tempofile.write(value.encode(encoding='utf-8'))
                case 'datetime':
                    tempofile.write(httpdate(value).encode(encoding='utf-8'))
                case _:
                    tempofile.write(jdumper(value).encode(encoding='utf-8'))
            tempofile.seek(0)
            return tempofile.read().decode(encoding='utf-8')
        pass

    def _ifstmt(self, exl, printer, vardict, xfunction):
        ifcond_true = False
        for ifcond in exl['children']:
            attrs = ifcond['attrs']
            match ifcond['ElementName'].lower():
                case 'ifcond':
                    setleftas = attrs.get('setleftas')
                    rightvar = attrs.get('right')
                    if (setleftas and rightvar) and (setleftas == rightvar):
                        raise XMLEqualsWarning('setleftas="" and right="" are equal this can lead to weird behavior')
                    if setleftas:
                        left = input('left>>>')
                        # vardict[setleftas] = left
                        self._edit_vardict(setleftas, left, 'String', vardict)
                        left = dict(value=[left], type='String')
                    else:
                        left = vardict.get(attrs.get('left'), self.__undef['value'])
                    if rightvar:
                        right = vardict.get(attrs['right'], self.__undef['value'])
                    else:
                        right = dict(value=[attrs.get('rightStr', '__undef')], type='String')
                    match attrs.get('equals', '__undef'):
                        case '==':
                            raise NotImplementedError
                        case '===':
                            ifcond_true = ifcond_true or (
                                (left['type'] == right['type'] and (
                                        self._to_string_from_object(left['value'], left['type']) ==
                                        self._to_string_from_object(right['value'], right['type'])))
                            )
                            pass
                    pass
                case 'ifbody':
                    if ifcond_true:
                        for exlc in ifcond['children']:
                            self._exec(exlc, printer, vardict, xfunction)
                        break
                case 'elsebody':
                    for exlc in ifcond['children']:
                        self._exec(exlc, printer, vardict, xfunction)
                    break
        return

    @staticmethod
    def _mkvar(name, value, type_, vardict):
        vardict[name] = dict(value=value, type=type_)

    def _exec(self, exl, printer, vardict, xfunction):
        if exl['xmlns'] != self.xmlns:
            return
        match (xmlname := exl['ElementName']):
            case 'xout':
                self._xout(exl['children'], 'lix', printer)
            case 'xecho':
                try:
                    value = vardict[exl['attrs']['var']]
                    self._xout(self._to_string(value), 'str', printer)
                except KeyError:
                    raise XKeyExrror('xecho has not a var="" set or that variable is not in the localscope') from None
            case 'select':
                dictvar = vardict[exl['attrs']['from']]
                xhr = (inx if (inx := exl['attrs'].get('index', False))
                       else vardict.get(exl['attrs'].get('indexvar', '__undef'),
                                        self.__undef)['value'][0])
                item = dictvar['value'][int(xhr)]
                pass
                # self._edit_vardict(
                #     exl['attrs']['varto'],
                #     dictvar['value'][int(exl['attrs']['index'])],
                #     dictvar['type'], vardict)
                self._mkvar(
                    exl['attrs']['varto'],
                    item['value'],
                    item['type'],
                    vardict)
                pass
            case 'xcall':
                returnto = self._callfunc(exl['attrs']['xname'], printer)
                if returnto is not None:
                    vardict[exl['attrs']['returnto']] = returnto
            case 'xfor':
                if bool(var := exl['attrs'].get('loopto')):
                    rgnx = vardict[var]['value']
                else:
                    rgnx = range(
                        int(exl['attrs']['start']),
                        int(exl['attrs']['stop']),
                        int(exl['attrs'].get('step', 1)))
                    rgnx = (dict(value=[f'{i}'], type='String') for i in rgnx)
                for var in rgnx:
                    self._edit_vardict(exl['attrs']['var'], var['value'], var['type'], vardict)
                    # vardict[] = var
                    for exlc in exl['children']:
                        self._exec(exlc, printer, vardict, xfunction)
            case 'xign':
                pass
            case 'help':
                Printer.out(printer, self.__helpstmt.get(
                    (stmt := (exl.get('stmt', 'help'))).lower(),
                    f'no help found for {stmt}\n\n{self.__helpstmt['help']}'))
            case 'If':
                self._ifstmt(exl, printer, vardict, xfunction)
            case 'if':
                self._ifstmt(exl, printer, vardict, xfunction)
            case 'xfunction':
                return
            case 'toString':
                setas = xmlas if (xmlas := exl['attrs'].get('setas')) else exl['attrs']['var']
                vardict[setas] = vardict[exl['attrs']['var']]
            case 'new':
                self._createnew(exl, vardict)
            case 'return':
                return vardict[exl['attrs']['var']]
            case 'autofill':
                for i in range(-5, 256):
                    self._edit_vardict(f'{i}', f'{i}', 'String', vardict)
            case 'desc':
                return
            case 'include':
                module = self.__modules[(importas := exl['attrs']['as'])] = \
                    XScripter.file_get_contents(
                        self.conf['cwd'] / (importsrc := exl['attrs']['src'])
                    ).setconf('__name', importsrc).xmlparse(
                    ).xmlrun(suppress=True)._xfunctions
                for xname, xfunc in module.items():
                    if xname == 'main':
                        continue
                    if self._xfunctions.get(f'{importas}.{xname}') is not None:
                        raise ValueError(f'{importas}.{xname} exxists already')
                    self._xfunctions[f"{importas}.{xname}"] = xfunc
                pass
            case 'xall':
                for xtag, helpstr in self.__helpstmt.items():
                    printer.out(f'<{xtag}>\n{helpstr}\n\n')
            case _:
                print(xmlname, 'is not a supported element, if this is intentional',
                      'please add it to an xignel element to suppress this warning')
                pass  # X IGN ore Element
        return None

    def _callfunc(self, xfunction, printer):
        xgfunction = self._xfunctions[xfunction]
        xgfunction['vardict'] = dict(__name=dict(value=[self.conf['__name']], type='String'))
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
        match type_:
            case 'xml':
                rtrn = lixt['xml']
            case 'lix':
                rtrn = split.join(lixt)
            case 'str':
                rtrn = lixt
            case _:
                raise XMLNotImplementedError
        printer.out(rtrn := (rtrn + end))
        return rtrn

    def xmlrun(self, *, return_=False, suppress=False):
        if not self.__openfor_run:
            raise Exception('ude a new XScripter')
        self.__openfor_run = False
        startdate = httpdate(started_at := utcnow())
        if not suppress:
            print('\nhello at', startdate)
        start_time = time.perf_counter()
        with (open(self.conf['out.txt'], 'wt', encoding='utf-8') as outfile,
              open(self.conf['dump.json'], 'wt', encoding='utf-8') as jdump):
            printer, jdump = Printer(outfile, self.conf['printconsole']), Printer(jdump)
            printer.out(httpdate(started_at)).out('\n').out('\n')
            try:
                self.conf['__name'] = \
                    (__name if
                     (__name := self.conf.get(
                         '__name', '__undef__'))
                     != '__undef__' else '__main__')
                self._xmlstart(self.__parsedata, printer=printer, toplvl=True)
                if self._ismain:
                    self._callfunc('main', printer)
            finally:
                jdump.out(jdumper(self.to_json(), indent=4))
                out_ = printer.return_()
                jdump_ = jdump.return_()
                end_time = time.perf_counter()
                elapsed_time = end_time - start_time
                if not suppress:
                    print('\nout', out_)
                    print('jdump', jdump_)
                    print(f"Elapsed time: {elapsed_time:.6f} seconds\n")
                if return_:
                    return out_, jdump_, elapsed_time
        return self

    def xmlparse(self):
        self.__parsedata = self._xmlparse_ai(self.scriptf)
        return self

    @classmethod
    def file_get_contents(cls, openxml, docsfile='help.toml'):
        n_ext = (xpath := pathlib.Path(openxml)).stem
        xpath = xpath.parent
        (opath := xpath / 'xout').mkdir(exist_ok=True)
        with open(openxml, 'rt', encoding='utf-8') as xml:
            clss = (cls(xml.read(), docsfile=docsfile).setconf('cwd', xpath)
                    .setconf('out.txt', f'{opath}/{n_ext}-out.txt')
                    .setconf('dump.json', f'{opath}/{n_ext}-dump.json'))
            return clss
        pass

    def setconf(self, key, val):
        self.conf[key] = val
        return self

    pass


if __name__ == '__main__':
    XScripter.file_get_contents('./xsrc/testfile.xml').xmlparse().xmlrun()
    # XScripter.file_get_contents('./xsrc/hello.xml').xmlparse().xmlrun()
    print('end')
pass
