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

for i in range(len(content1)):
    content1[i] = content1[i].replace("v0", "#var")
print(content1)

for i in range(len(content2)):
  content2[i] = content2[i].replace("v1", "#var")


diff = difflib.unified_diff(content1, content2)
for line in list(diff):
    print(line)

