#!/usr/bin/python

import sys
import os
import re
import glob
import shutil
import difflib
import argparse
import tempfile
from filecmp import *
from class_parser import ClassParser
from subprocess import call, STDOUT
from fuzzy_match import algorithims
from androguard.core.bytecodes import apk

temp1 = ""
temp2 = ""
apk_name = ""

# fileter_word = ["field", "line", "const", "0x", "local", "nop", "array", "move", "annotation"]
fileter_word = ["line", "0x"]

key_words = ["invoke", "method"]


def apk_parse():
    global temp1, temp2, apk_name
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

    # Make sure the APKs exist.
    exists(args.apk1)
    exists(args.apk2)

    # Check the temporary folder exists & clear it.
    folder_exists(args.output, True)

    # get APK name
    apk_name = get_apk_name(args.apk1).split('-')[0]

    # Individual folders for each APK.
    temp1 = args.output + "/" + apk_name + '/1/'
    temp2 = args.output + "/" + apk_name + '/2/'

    # check folder exist
    folder_exists(temp1, True)
    folder_exists(temp2, True)

    # utilize apktool to decompose both apk
    apktoolit(args.apk1, temp1)
    apktoolit(args.apk2, temp2)

    # merge two smail folders
    merge_smali_folders(temp1)
    merge_smali_folders(temp2)

    temp1 = os.path.join(temp1, "smali/")
    temp2 = os.path.join(temp2, "smali/")


# get apk name with version
def get_apk_name(apk_path):
    return apk_path.split("/")[-1].split('.')[0]


# get package name
def get_package_name(filepath):
    # a = apk.APK(filepath)
    package_name = apk.APK(filepath).get_package()
    package_name = package_name.replace('.', '/')
    return package_name


# use apktool to disassemble apk files
def apktoolit(file, dir):
    print("Running apktool against '" + file + "'")
    call(["apktool", "d", "-r", "-f", "-o", dir, file], stdout=open(os.devnull, 'w'), stderr=STDOUT)
    print("[OK]")


def merge_smali_folders(folder):
    print("Merging additional smali folders")
    target = os.path.join(folder, "smali")
    for name in glob.glob(folder + "smali_classes*"):
        print("\t" + name + " > " + target)
        merge_folders(name, target)
    print("[OK]")


def merge_folders(root_src_dir, root_dst_dir):
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
    class_pair_file_name = "./class_pair/classPairOutput_{}.txt".format(apk_name)
    file = open(class_pair_file_name)
    lines = file.readlines()
    file.close()

    existing_file_count = 0
    total_class_count = 0
    for line in lines:
        total_class_count += 1
        # read old class file
        left_class = line.split(":")[0].replace(".", "/") + ".smali"
        # read new corresponding class file
        right_class = line.split(":")[1].replace(".", "/") + ".smali"
        # read the class pair similarity
        similarity = float(line.split(":")[-2])
        # read the threshold for the class pair
        threshold = float(line.split(":")[-1])
        file_path1 = os_path1 + left_class
        file_path2 = os_path2 + right_class

        if exists(file_path1) and exists(file_path2):
            existing_file_count += 1
            if similarity > threshold:
                old_class_profile = ClassParser(file_path1).class_parser()
                new_class_profile = ClassParser(file_path2).class_parser()
                diff_result = generate_diff_result(old_class_profile, new_class_profile)
                print_diff_result(diff_result, file_path1, file_path2)

    print("count of existing files: ", existing_file_count)
    print("count of total class files: ", total_class_count)


def print_diff_result(diff_result, old_file_path, new_file_path):
    if diff_result:
        print('------------------------------------------------------------------------------------------------------')
        print('[', old_file_path, ']')
        print('[', new_file_path, ']')
        for line in diff_result:
            print(line, end='')


def generate_diff_result(old_class_profile, new_class_profile):
    diff_result = []
    for name in old_class_profile['class_method']:
        file1 = old_class_profile['class_method'][name]
        if name in new_class_profile['class_method']:
            file2 = new_class_profile['class_method'][name]
            diff_result = diff_result + filter_diff_result(list(difflib.unified_diff(file1, file2)))
    return diff_result


def filter_diff_result(diff_result):
    filtered_diff_result = []
    for line in diff_result:
        if line[0] == '-' or line[0] == '+':
            if not is_contain_filter_word(line):
                filtered_diff_result.append(line)
    if len(filtered_diff_result) == 2:
        return []
    else:
        return filtered_diff_result


def is_contain_key_word(line):
    for word in key_words:
        if word in line:
            return True
    return False


def is_contain_filter_word(line):
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


def folder_exists(path, clean=False):
    if clean and os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)


if __name__ == "__main__":
    apk_parse()
    class_compare()
