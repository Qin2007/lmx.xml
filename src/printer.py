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


pass
