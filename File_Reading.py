from __future__ import print_function
import os

f = open(os.path.join(os.getcwd()+"\output\lines_of_code.dat"), "r")
data = f.readlines()
for line in data:
    data[data.index(line)] = line.replace('\n','')

print(data)

print(data[1][1])
print(data[2][1])
print(data[3][1])
