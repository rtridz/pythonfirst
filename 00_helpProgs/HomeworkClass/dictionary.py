input = open('ru-en.txt')
output = open('en-ru.txt', 'w')

tempList = {}
for line in input:
    words = line.strip().split(' - ')
    en = words[0]
    lat = words[1].split(', ')
    for key in lat:
        if key in tempList:
            tempList[key].append(en)
        else:
            tempList[key] = [en]
input.close()

for key in tempList:
    tempList[key].sort()


for lat in sorted(tempList):
    output.write(lat + ' - ' + ', '.join(tempList[lat]) + '\n')

output.close()