#!/usr/bin/python

import difflib

# filter_word = ["field", "line", "const", "0x", "local", "nop", "array", "move", "annotation"]
filter_word = ['.line', '.local']


class ClassParser:
    def __init__(self, filepath):
        file = open(filepath, 'r', encoding='utf8', errors='ignore')
        self.file_data = file.read().splitlines(1)
        self.file_data = preprocessing(self.file_data)
        self.class_file_map = {'class_name': [], 'class_super': [], 'class_source': [], 'class_field': [],
                               'class_implements': [], 'class_annotation': [], 'class_method': {}}
        file.close()

    def class_parser(self):
        i = 0
        while i < len(self.file_data):
            if self.file_data[i].startswith('.class'):
                self.class_file_map['class_name'].append(self.file_data[i])
                i += 1
            elif self.file_data[i].startswith('.super'):
                self.class_file_map['class_super'].append(self.file_data[i])
                i += 1
            elif self.file_data[i].startswith('.source'):
                self.class_file_map['class_source'].append(self.file_data[i])
                i += 1
            elif self.file_data[i].startswith('.field'):
                self.class_file_map['class_field'].append(self.file_data[i])
                i += 1
                # while not is_end_of_element(i, self[i], len(self)):
                #     self.class_file_map[['class_field'].append(self[i])
                #     i += 1
            elif self.file_data[i].startswith('.implements'):
                self.class_file_map['class_implements'].append(self.file_data[i])
                i += 1
                # while not is_end_of_element(i, self[i], len(self)):
                #     self.class_file_map[['class_implements'].append(self[i])
                #     i += 1
            elif self.file_data[i].startswith('.annotation'):
                self.class_file_map['class_annotation'].append(self.file_data[i])
                i += 1
                # while not is_end_of_element(i, self[i], len(self)):
                #     self.class_file_map[['class_annotation'].append(self[i])
                #     i += 1
            elif self.file_data[i].startswith('.method'):
                # class_file['class_method'].append(file[i])
                method_key = self.file_data[i]
                method_content = [self.file_data[i]]
                i += 1
                while i < len(self.file_data) and is_not_end_of_element(self.file_data[i]):
                    method_content.append(self.file_data[i])
                    i += 1
                self.class_file_map['class_method'][method_key] = method_content
            else:
                i += 1
        return self.class_file_map


def preprocessing(class_file):
    class_file = remove_useless_element(class_file)
    class_file = obfuscation_resistance(class_file)
    return class_file


def remove_useless_element(class_file):
    new_class_file = []
    for line in class_file:
        if line != '\n':
            new_class_file.append(line)

    class_file = new_class_file
    new_class_file = []
    for line in class_file:
        if is_not_contain_filter_word(line):
            new_class_file.append(line)
    return new_class_file


def obfuscation_resistance(class_file):

    return class_file


def is_not_end_of_element(line):
    if line.startswith('.class') or line.startswith('.super') or line.startswith('.source') or line.startswith(
            ".implements") or line.startswith('.annotation') or line.startswith('.method') or line.startswith('.field'):
        return False
    return True


def is_not_contain_filter_word(line):
    for word in filter_word:
        if word in line:
            return False
    return True


if __name__ == '__main__':
    old_class_profile = ClassParser('BindingFailedResolution1.smali').class_parser()
    new_class_profile = ClassParser('BindingFailedResolution2.smali').class_parser()
    diff_result = []

    for name in old_class_profile['class_method']:
        file1 = old_class_profile['class_method'][name]
        if name in new_class_profile['class_method']:
            file2 = new_class_profile['class_method'][name]
            diff_result = diff_result + list(difflib.unified_diff(file1, file2))

    for d in list(diff_result):
        if d[0] == '-' or d[0] == '+':
            print(d, end="")
