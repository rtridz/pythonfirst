class Player:
    score = 3
    rank = "Pro"

    def getScore(self):
        return self.score

    def setScore(self, value):
        self.score = value


p=Player()

print(p.getScore())

p.setScore(10)
print(p.getScore())

def execution():
    return "Execution"

setattr(p, "command", execution)
type(p)
