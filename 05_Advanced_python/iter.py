class num_generator():
    def __init__(self, max):
        self.size = max
        self.num = 1

    def __iter__(self):
        return self

    def __next__(self):
        if self.num <= self.size:
            current = self.num
            self.num += 1
            return current ** 2
        else:
            raise StopIteration()


for val in num_generator(4):
    print(val)

# out:
# 	1
# 	4
# 	9
# 	16