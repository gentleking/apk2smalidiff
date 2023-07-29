import difflib
import os

def reader(file):
    f = open(file, 'r', encoding='utf8', errors='ignore')

    data = f.read()
    f.close()
    return data

filepath1 = "file1.txt"
filepath2 = "file2.txt"

content1 = reader(filepath1).splitlines(1)
content2 = reader(filepath2).splitlines(1)

diff = difflib.unified_diff(content1, content2)
for line in list(diff):
    print(line)

