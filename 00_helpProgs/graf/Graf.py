class Graf:

    def __init__(self, V, E):
        self.v = set(V)
        self.e = set(E)

    def add_vertex(self, v):
        self.v.add(v)

    def add_edge(self, v1, v2):
        self.v.add(v1)
        self.v.add(v2)
        self.e.add((v1, v2))

    def has_edge(self, v1, v2):
        return (v1, v2) in self.e

    def __str__(self):
        return "%s; %s" % (self.v, self.e)
# v = [1, 2, 3, 4]
# e = [(1, 2), (2, 3), (2, 4)]
g = Graf()

print(g)

g.add_vertex(6)
print(g)

g.add_edge(2, 6)
print(g)


if g.has_edge(1,2):
    print(1)
else:
    print(2)

if g.has_edge(1,4):
    print(1)
else:
    print(2)

