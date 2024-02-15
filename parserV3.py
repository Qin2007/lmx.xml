from pprint import pprint

from bs4 import BeautifulSoup

from printer import Printer


# noinspection PyTypeChecker
def parse_function(xmlfunc, xmldict):
    for x in xmlfunc.children:
        if x.name == 'xfunction' and x.attrs['xname'] != 'main':
            xmldict['xfunctions'][x.attrs['xname']] = x

            parse_function(x, xmldict)
        else:
            xmldict['xout'].append(repr(x))
    return


def xmlparse(xmlstring: str, stdout='output.txt'):
    with open(stdout, 'wt') as stdout_:
        out = Printer(stdout_)
        xmldict = dict(xfunctions=dict(), xout=list())

        # noinspection PyTypeChecker
        @lambda _: _()
        def wrapper():
            soup = BeautifulSoup(xmlstring, features='xml')
            x = [i for i in soup.children][0]
            if x.name == 'xfunction':
                xmldict['xfunctions'][x.attrs['xname']] = x
                parse_function(x, xmldict)
            else:
                return False
            return True

        pass
    return wrapper, xmldict


def main():
    with open('testfile.xml', 'rt') as xmlhttp:
        print('exited with bool', (dixt := xmlparse(xmlhttp.read()))[0])
    with open('xmldata.txt', 'wt') as xmlhttp:
        pprint(dixt[1], stream=xmlhttp)
        xmlhttp.write('<!DOCTEXT >')
    pass


if __name__ == '__main__':
    main()
pass
