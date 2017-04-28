"""
Generator that makes random unity IDs.  Not based of existing data, so no markov chain generation n stuff.
Useful for testing.

Args:
    N/A

Authors:
    Samuel Schoeneberger
"""

import random
import string

# csc216-002-P2-096:spschoen razeitle


def gen_unity_id():
    unity_id = ""
    length = random.randrange(4, 8)
    for i in range(length):
        unity_id += random.choice(string.ascii_lowercase)
    if random.randrange(1, 6) > 4:
        longo = list(unity_id)
        longo[len(longo) - 1] = str(random.randrange(1, 9))
        unity_id = "".join(longo)
    return unity_id

f = open("students.txt", "w")

length_max = random.randrange(50, 150)

for i in range(length_max):
    if length_max > 99:
        base = "csc216-002-P1-" + str(i).zfill(3)
    else:
        base = "csc216-002-P1-" + str(i).zfill(2)

    users = ""
    weight = random.random()
    if weight >= .9:
        users = gen_unity_id() + " " + gen_unity_id() + " " + gen_unity_id()
    elif weight >= .75:
        users = gen_unity_id() + " " + gen_unity_id()
    else:
        users = gen_unity_id()

    f.write(base + ":" + users + "\n")
