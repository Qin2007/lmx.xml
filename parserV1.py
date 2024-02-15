from html.entities import name2codepoint
from html.parser import HTMLParser


class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        print("Start tag:", repr(tag))
        for attr in attrs:
            print("     attr:", repr(attr))

    def handle_endtag(self, tag):
        print("End tag  :", repr(tag))

    def handle_data(self, data):
        print("Data     :", repr(data))

    def handle_comment(self, data):
        print("Comment  :", repr(data))

    def handle_entityref(self, name):
        c = chr(name2codepoint[name])
        print("Named ent:", repr(c))

    def handle_charref(self, name):
        if name.startswith('x'):
            c = chr(int(name[1:], 16))
        else:
            c = chr(int(name))
        print("Num ent  :", repr(c))

    def handle_decl(self, data):
        print("Decl     :", repr(data))


with open('testfile.xml') as xmlhttp:
    xmltext = xmlhttp.read()
MyHTMLParser().feed(xmltext)
