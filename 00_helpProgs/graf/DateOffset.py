class DateOffset:
    def __init__(self):
        self.start = 0
    def _get_offset(self):
        self.start += 5
        return self.start

    offset = property(_get_offset)




d=DateOffset()
print(d.offset)

