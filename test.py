import difflib
import os

from fuzzy_match import algorithims

diff_ratios = []


def main():
    class_compare()


def class_compare():
    os_path1 = "/tmp/apkdiff/1/smali/"
    os_path2 = "/tmp/apkdiff/2/smali/"
    file = open("classPairOutput.txt")
    lines = file.readlines()
    left_class = ""
    right_class = ""
    similarity = 0
    count = 0
    total_class = 0
    for line in lines:
        total_class += 1
        left_class = line.split(":")[0].replace(".", "/") + ".smali"
        right_class = line.split(":")[1].replace(".", "/") + ".smali"
        similarity = line.split(":")[-1]
        file_path1 = os_path1 + left_class
        file_path2 = os_path2 + right_class
        if exists(file_path1) and exists(file_path2):
            count += 1
            # print("[" + os_path1 + left_class + "]")
            # print("[" + os_path2 + right_class + "]")
            # print("similarity: " + similarity)
            content1 = reader(file_path1).splitlines(1)
            content2 = reader(file_path2).splitlines(1)
            # print(content1)
            # print(content2)
            diff = difflib.unified_diff(content1, content2, file_path1, file_path2)
            # print_diff(list(diff))
            filter(list(diff))
    file.close()
    print("count of existing files: ", count)
    print("total class is: ", total_class)

def filter(lines):
    # print(lines)
    for line in lines:
        if(isContain(line)):
            print(line, end="")


def isContain(line):
    return not ("field" in line or "line" in line)
    # return False


def reader(file):
    f = open(file, 'r', encoding='utf8', errors='ignore')

    data = f.read()
    f.close()
    return data


def exists(file):
    if not os.path.isfile(file):
        print("'{}' does not exist.".format(file))
        return False
    return True


if __name__ == "__main__":
    main()
