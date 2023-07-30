#!/usr/bin/python

import difflib
import os
import sys
import os
import zipfile
from filecmp import *
from subprocess import call, STDOUT
import shutil
import glob
import re
import argparse
import difflib
import tempfile
from androguard.core.bytecodes import apk
from fuzzy_match import match
from fuzzy_match import algorithims
# as ps


# diff_ratios = []

temp1 = ""
temp2 = ""
apkName = ""

fileter_word = ["field", "line", "const", "0x", "local", "nop", "array", "move"]

key_words = ["invoke", "method"]


def main():
    apk_parse()
    class_compare()


def apk_parse():
    global temp1, temp2, apkName
    print("")
    print("\t\t\t apktool")
    print("")

    parser = argparse.ArgumentParser(description='Diff two versions of an APK file.')
    parser.add_argument('apk1', metavar='apk1', help='Location of the first APK.')
    parser.add_argument('apk2', metavar='apk2', help='Location of the second APK.')
    parser.add_argument('-c', '--cleanup', action='store_true', help='Remove all extracted files after computation.')
    parser.add_argument('-m', '--meld', action='store_true', help='Open meld to compare directories after.')
    parser.add_argument('-o', '--output', default=os.path.join(tempfile.gettempdir(), 'apkdiff'),
                        help='The location to output the extracted files to.')
    parser.add_argument('-u', '--unique', action='store_true',
                        help='By default, only differences in common files are printed. If -u is enabled, unique files are printed too')

    global args
    args = parser.parse_args()

    # print(args)

    # Make sure the APKs exist.
    exists(args.apk1)
    exists(args.apk2)

    # Check the temporary folder exists & clear it.
    folderExists(args.output, True)

    # args.apk1 and args.apk2 are input args
    packageName1 = getPackageName(args.apk1)
    packageName2 = getPackageName(args.apk2)

    # get apk name with version
    apkName1 = getApkName(args.apk1)
    apkName2 = getApkName(args.apk2)

    # APK name
    apkName = apkName1.split('-')[0]

    # Individual folders for each APK.
    # temp1 = os.path.join(args.output, '/', apkName1, '/1/')
    # temp2 = os.path.join(args.output, '/', apkName1, '/2/')
    temp1 = args.output + "/" + apkName + '/1/'
    temp2 = args.output + "/" + apkName + '/2/'
    
    # check folder exist
    folderExists(temp1, True)
    folderExists(temp2, True)

    # utilize apktool to decompose both apk
    apktoolit(args.apk1, temp1)
    apktoolit(args.apk2, temp2)

    # merge two smail folders
    mergesmalifolders(temp1)
    mergesmalifolders(temp2)

    temp1 = os.path.join(temp1, "smali/")
    temp2 = os.path.join(temp2, "smali/")
    # print(temp1, temp2)


def getApkName(apkname):
    apkn = apkname.split("/")[-1]
    apkn = apkn.split(".")[0]
    return apkn


# get package name
def getPackageName(filepath):
    a = apk.APK(filepath)
    packageName = a.get_package()
    packageName = packageName.replace('.', '/')
    # print("package name: " + packageName)
    return packageName


# use apktool to disassemble apk files
def apktoolit(file, dir):
    print("Running apktool against '" + file + "'")
    call(["apktool", "d", "-r", "-f", "-o", dir, file], stdout=open(os.devnull, 'w'), stderr=STDOUT)
    print("[OK]")


def mergesmalifolders(folder):
    print("Merging additional smali folders")
    target = os.path.join(folder, "smali")
    for name in glob.glob(folder + "smali_classes*"):
        print("\t" + name + " > " + target)
        mergefolders(name, target)
    print("[OK]")


def mergefolders(root_src_dir, root_dst_dir):
    for src_dir, dirs, files in os.walk(root_src_dir):
        dst_dir = src_dir.replace(root_src_dir, root_dst_dir, 1)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                os.remove(dst_file)
            shutil.move(src_file, dst_dir)


def class_compare():
    os_path1 = temp1
    os_path2 = temp2
    # print("apkname: ", apkName)
    fileName = "classPairOutput_" + apkName + ".txt"
    # file = open("classPairOutput.txt")
    file = open(fileName)
    lines = file.readlines()
    left_class = ""
    right_class = ""
    similarity = 0
    count = 0
    class_count = 0
    for line in lines:
        class_count += 1
        left_class = line.split(":")[0].replace(".", "/") + ".smali"
        right_class = line.split(":")[1].replace(".", "/") + ".smali"
        similarity = float(line.split(":")[-1])
        file_path1 = os_path1 + left_class
        file_path2 = os_path2 + right_class
        if exists(file_path1) and exists(file_path2):
            count += 1
            if similarity > 0.8:
                content1 = reader(file_path1).splitlines(1)
                content2 = reader(file_path2).splitlines(1)
                
                content1 = preprocessing(content1)
                content2 = preprocessing(content2)
                diff = difflib.unified_diff(content1, content2, file_path1, file_path2)
                filter(list(diff))
    file.close()

    print("count of existing files: ", count)
    print("count of total class files: ", class_count)


def preprocessing(content):
    var = ["p0", "p1", "p2", "p3", "v0", "v1", "v2", "v3", "v4", "v5"]
    for i in range(0, len(content)):
        for v in var:
            content[i] = content[i].replace(v, '#var')
    return content


def filter(lines):
    if not lines:
        return
    # else: 
    #     print(lines)

    filter_lines = []
    left_class = lines[0]
    right_class = lines[1]
    diff_lines = []
    flag = False

    # every @@ diff result to analyse
    for i in range(3, len(lines)):
        if "@@" in lines[i]:

            # generate diff result in a basic block
            diff_lines = generate_diff_lines(filter_lines)

            # analyze the diff result
            analyze_lines(diff_lines)

            if diff_lines:
                flag = True
            filter_lines = []

        filter_lines.append(lines[i])
    
    if flag:
        print(left_class, end="")
        print(right_class)


# analyze the difference of lines
def analyze_lines(diff_lines):
    for line in diff_lines:
        print(line, end="")
    return


# generate the diff lines
def generate_diff_lines(filter_lines):
    if not filter_lines:
        return
    diff_lines = []

    if is_contain_diff_result(filter_lines) and generate_diff_ratio(filter_lines) < 0.9:
        for line in filter_lines:
            # whether contain filter word
            if not is_contain_filter_word(line):
                #if is_contain_key_word(line):
                # whether line is diff result
                if line[0] == '+' or line[0] == '-':
                    diff_lines.append(line)
                # print(line, end="")
    return diff_lines


def is_contain_key_word(line):
    for word in key_words:
        if word in line:
            return True
    return False


def generate_diff_ratio(filter_lines):
    add_line = ""
    minu_line = ""
    for line in filter_lines:
        if line[:1] == "+":
            add_line += line
        elif line[:1] == "-":
            minu_line += line
    diffratio = algorithims.cosine(add_line, minu_line)
    return float(diffratio)


def is_contain_diff_result(filter_lines):
    for line in filter_lines:
        if line and (line[0] == '-' or line[0] == '+'):
            return True
    return False


def is_contain_filter_word(line):
    # case1: line is none
    if not line:
        return True
    
    # case2: blank line
    substr = line[1:len(line)-1]
    if not substr:
        return True
    
    # case3: contain filter word
    for word in fileter_word:
        if word in line:
            return True

    return False


def reader(file):
    f = open(file, 'r', encoding='utf8', errors='ignore')

    data = f.read()
    f.close()
    return data


def exists(file):
    if not os.path.exists(file):
        # print("'{}' does not exist.".format(file))
        print("No existing file: ", file)
        return False
    return True


def folderExists(path, clean=False):
    if clean and os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)


if __name__ == "__main__":
    main()
