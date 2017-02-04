import os

f = open(os.path.join(os.getcwd()+"/test.txt"), "r")

data = f.readlines()

for line in data:
    linesOfCode = line.replace("\n","").split(") ")[1]
    print "Lines:",linesOfCode

print len(data)

f.close()
