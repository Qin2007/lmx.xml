from pprint import pprint
from xml.etree.ElementTree import Element

from defusedxml import ElementTree

from printer import Printer


def parse_children(elements, xmldict,output=''):
    for element in elements:
        if element.tag == 'xout':
            xmldict['xout'].append(ElementTree.tostring(element, 'unicode'))
        elif element.tag == 'xfunction':
            key, val = [(k, v) for k, v in element.items() if k == 'xname'][0]
            xmldict['xfunctions'][val] = element
        else:
            parse_children(element, xmldict,output=f'>')
    pass


def xmlparse(xmlstring: str, stdout='output.txt'):
    with open(stdout, 'wt') as stdout_:
        out = Printer(stdout_)
        xmldict = dict(xfunctions=dict(), xout=list())
        if (xtag := ElementTree.fromstring(xmlstring)).tag == 'xfunction':
            key, val = [(k, v) for k, v in xtag.items() if k == 'xname'][0]
            xmldict['xfunctions'][val] = xtag
            parse_children((x for x in xtag), xmldict)
        else:
            out.out(xmlstring)
        print('out', out.return_())
        with open('xmldata.txt', 'wt') as dixt:
            pprint(xmldict,stream=dixt)
            dixt.write('<!DOCTEXT>')
        pass
    pass


def main():
    with open('testfile.xml') as xmlhttp:
        xmlparse(xmlhttp.read())
    (lambda x: x)(Element)


if __name__ == '__main__':
    main()
pass
