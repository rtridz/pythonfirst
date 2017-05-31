class ExternalStorage:
    __slots__ = ("attribute_name",)
    __storage = {}
    def __init__(self, attribute_name):
        self.attribute_name = attribute_name
    def __set__(self, instance, value):
        self.__storage[id(instance), self.attribute_name] = value
    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return self.__storage[id(instance), self.attribute_name]


class Point:
    __slots__ = ()
    x = ExternalStorage("x")
    y = ExternalStorage("y")
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


print(Point(1,2).x)
# p2=Point(3,4)