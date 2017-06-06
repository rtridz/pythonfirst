import sys

word = sys.stdin.readline().rstrip()
filename = sys.stdin.readline().rstrip()

try:
  with open(filename, "rb") as fh:
    while True:
      current = fh.readline()
      if not current:
          break
      if (word in current ):
          print("find: {0} {1}".format(filename,word))
except :
    pass