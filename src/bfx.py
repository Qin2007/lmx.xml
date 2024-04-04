import re

from src.printer import Printer


class Byte:
    def __init__(self, byte: int):
        self.__byte = byte

    @property
    def byte(self):
        self.__byte = (self.__byte % 256)
        return self.__byte

    @byte.setter
    def byte(self, value):
        self.__byte = value

    def addone(self):
        self.byte += 1

    def rmvone(self):
        self.byte -= 1

    def __int__(self):
        return self.byte

    def __repr__(self):
        return f'Byte({self.byte})'

    def __format__(self, format_spec):
        match format_spec:
            case 'utf-8':
                return chr(int(self))
            case 'byte':
                return int(self)
            case 'x':
                return hex(int(self))
            case 'b':
                return bin(int(self))
        pass

    pass


def parse(bfx: str, bfout='bfstdout.txt', *, xtended_syntax=False):
    if xtended_syntax:
        raise NotImplementedError
    bfx = re.sub('[^.,<>\\-+\\[\\]]', '', bfx)
    array: list[Byte] = [Byte(0) for _ in range(30_000)]
    index = 0
    pointer = 0
    bfxl = len(bfx)  # BrainFuck eXtended Lengthy
    with (open(bfout, 'wt') as bfout_):
        printer = Printer(bfout_).out('hello from pythonBFx.parse/0.0.0\n')
        while bfxl > pointer >= 0:
            match (bfx[pointer]):
                case '+':
                    array[index].addone()
                case '-':
                    array[index].rmvone()
                case '.':
                    printer.out(f'{array[index]:utf-8}')
                case '>':
                    index += 1
                case '<':
                    index -= 1
                case '[':
                    pass
                case ']':
                    pass

        print('written', printer.out('\n').return_(), 'to output')
    pass


if __name__ == '__main__':
    with open('brainfuck.bf', 'rt') as bf:
        parse(bf.read())
pass
