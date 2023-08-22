#!/usr/bin/python
import difflib

filter_word = ["field", "line", "const", "0x", "local", "nop", "array", "move", "annotation"]

def is_end_of_element(index, line, max_len):
    head = line.split(' ')[0]
    # print(head)
    if index >= max_len:
        return True
    return head == '.class' or head == '.super' or head == '.source' or head == '.implements' or \
        head == '.annotation' or head == '.method' or head == '.field'


def init_class_map(class_dict):
    class_dict['class_name'] = []
    class_dict['class_super'] = []
    class_dict['class_source'] = []
    class_dict['class_field'] = []
    class_dict['class_implements'] = []
    class_dict['class_annotation'] = []
    class_dict['class_method'] = {}


class ClassParser:
    def __init__(self):
        pass

    # @staticmethod
    def class_parser(self, file):
        i = 0
        index = ''
        class_file = {}
        init_class_map(class_file)
        while i < len(file):
            if file[i].split(' ')[0] == '.class':
                class_file['class_name'].append(file[i])
                i += 1
            elif file[i].startswith('.super'):
                class_file['class_super'].append(file[i])
                i += 1
            elif file[i].startswith('.source'):
                class_file['class_source'].append(file[i])
                i += 1
            elif file[i].split(' ')[0] == '.field':
                # print('field')
                class_file['class_field'].append(file[i])
                i += 1
                while not is_end_of_element(i, file[i], len(file)):
                    class_file['class_field'].append(file[i])
                    i += 1
            elif file[i].split(' ')[0] == '.implements':
                class_file['class_implements'].append(file[i])
                i += 1
                while not is_end_of_element(i, file[i], len(file)):
                    class_file['class_implements'].append(file[i])
                    i += 1
            elif file[i].split(' ')[0] == '.annotation':
                # print('annotaion')
                class_file['class_annotation'].append(file[i])
                i += 1
                while not is_end_of_element(i, file[i], len(file)):
                    class_file['class_annotation'].append(file[i])
                    i += 1
            elif file[i].split(' ')[0] == '.method':
                # class_file['class_method'].append(file[i])
                method_key = file[i]
                method_content = [file[i]]
                # method_dict = {}
                i += 1
                while not is_end_of_element(i, file[i], len(file)):
                    method_content.append(file[i])
                    i += 1
                    if i >= len(file):
                        break
                # method_dict[method_key] = method_content
                # class_file['class_method'].apppend(method_dict)
                class_file['class_method'][method_key] = method_content
            else:
                i += 1
        return class_file


def main():
    f = open('BindingFailedResolution1.smali', 'r', encoding='utf8', errors='ignore')
    f2 = open('BindingFailedResolution2.smali', 'r', encoding='utf8', errors='ignore')
    data = f.read().splitlines(1)
    data2 = f2.read().splitlines(1)
    f.close()
    f2.close()
    # class_file_parser = ClassParser()
    class_file = ClassParser().class_parser(data)
    class_file2 = ClassParser().class_parser(data2)
    diff_result = []
    print(class_file['class_method'])
    print(class_file2['class_method'])
    file1 = list(class_file['class_method'])
    file2 = list(class_file2['class_method'])
    # print(file1, file2)

    # diff = difflib.unified_diff(class_file['class_name']), class_file2['class_name']
    for name in class_file['class_method']:
        file1 = class_file['class_method'][name]
        if name in class_file2['class_method']:
            file2 = class_file2['class_method'][name]
            # d_result = list(difflib.unified_diff(file1, file2))
            diff_result = diff_result + list(difflib.unified_diff(file1, file2))
            # print(name)

    # diff = difflib.unified_diff(file1, file2)
    print(list(diff_result))
    for d in list(diff_result):
        if parser_filter(d):
            print(d, end="")
    # print(diff_result)


def parser_filter(line):
    if line == ' ' or line == '':
        return False
    if not is_contain_filter_word(line):
        if line[0] == '-' or line[0] == '+':
            if line[1:-1] != '':
                return True
    return False


def is_contain_filter_word(line):
    for word in filter_word:
        if word in line:
            return True
    return False


if __name__ == '__main__':
    main()
