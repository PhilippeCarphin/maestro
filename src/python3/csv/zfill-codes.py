#!/usr/bin/python3

path = "message_codes.csv"

with open(path, "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if i < 3:
        continue
    cells = line.split("\t")
    code = cells[0][0]+cells[0][1:].zfill(3)
    cells[0] = code
    lines[i] = "\t".join(cells)

with open(path, "w") as f:
    f.write("".join(lines))
