class Printer:
    def __init__(self, openf):
        self.openf = openf
        self.total = 0

    def out(self, strx: str):
        self.openf.write(strx)
        self.total += len(strx.encode())
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
