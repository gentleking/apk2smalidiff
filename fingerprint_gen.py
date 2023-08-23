import os
import zipfile
import glob
from loguru import logger
from config import ARTIFACT_TYPE
import sh
import collections
from pathlib import Path
import constants


class Generator:
    app_exclude_list = ['androidx/', 'android/support/', 'com/android/', 'com/google/', 'javax/', 'okhttp3/']

    def __init__(self, artifact_type, artifact_path, artifact_group, artifact_name):
        self.artifact_type = artifact_type
        self.artifact_path = artifact_path

        self.artifact_group = artifact_group
        self.artifact_name = artifact_name

        if self.artifact_type == ARTIFACT_TYPE.APK:
            self.extract_path = os.path.join(os.path.dirname(__file__), 'tmp/' + os.path.basename(artifact_path))
        else:
            self.extract_path = artifact_path + '.extract'

        self.module_fingerprints = collections.defaultdict(dict)
        self.extract_fingerprints()

    def extract_fingerprints(self):
        java_code_path = None

        try:
            if not os.path.exists(self.extract_path):
                # unpack aar with unzip
                if self.artifact_type == ARTIFACT_TYPE.AAR:
                    with zipfile.ZipFile(self.artifact_path, 'r') as zip_ref:
                        zip_ref.extractall(self.extract_path)
                elif self.artifact_type == ARTIFACT_TYPE.APK:
                    apktool = sh.Command('apktool')
                    apktool('d', self.artifact_path, '-o', self.extract_path)
                else:
                    logger.debug('File type not specified: %s' % self.artifact_path)
                    return

            if self.artifact_type == ARTIFACT_TYPE.AAR:
                classes_jar_path = os.path.join(self.extract_path, 'classes.jar')
                if not os.path.exists(classes_jar_path):
                    return

                # convert classes.jar to smali as well
                try:
                    d8 = sh.Command('d8')
                    dxed_path = classes_jar_path + '.tmp.jar'
                    d8('--output', dxed_path, classes_jar_path)
                except Exception as e:
                    print(e)
                    print('trying dx ...')

                    dx = sh.Command('dx')
                    dxed_path = classes_jar_path + '.tmp.jar'
                    dx('--dex', '--min-sdk-version=26', '--output=' + dxed_path, classes_jar_path)

                java_code_path = os.path.join(self.extract_path, 'java_code')
                apktool = sh.Command('apktool')
                apktool('d', dxed_path, '-f', '-o', java_code_path)

                sh.rm(dxed_path)
            else:
                java_code_path = self.extract_path

            if not os.path.isdir(java_code_path):
                return

            for smali_dir in glob.glob(os.path.join(java_code_path, 'smali*')):
                for root, subdirs, files in os.walk(smali_dir):
                    for smali_file in files:
                        if not smali_file.endswith('.smali'):
                            continue

                        smali_full_path = os.path.join(root, smali_file)
                        smali_relative_path = smali_full_path[smali_full_path.find(smali_dir) + len(smali_dir) + 1:]

                        module_name = 'dummy-root'
                        if '/' in smali_relative_path:
                            depth = smali_relative_path.count('/')
                            # roll down to 4 if depth > 4
                            module_name = '/'.join(smali_relative_path.split('/')[:min(4, depth)])

                        if any([module_name.startswith(ex) for ex in Generator.app_exclude_list]):
                            continue

                        # R shows up in app, but not in library
                        if '/R$' in smali_relative_path:
                            continue

                        # reverse D8 optimization
                        if 'ExternalSyntheticLambda' in smali_relative_path:
                            continue

                        self.parse_smali(module_name, smali_full_path, smali_relative_path)

            import shutil
            if self.artifact_type == ARTIFACT_TYPE.APK:
                shutil.rmtree(self.extract_path)
        except Exception as e:
            print(e)

    def normlize_types(self, tline):
        parts = []
        if len(tline) < 1:
            return parts

        i = 0
        while i < len(tline):
            j = i
            while j < len(tline):
                if tline[j] == ';' or tline[i:j + 1] in constants.PREDEFINED_TYPE_DICT:
                    break
                j += 1

            part = tline[i:j + 1]
            parts.append(chr(ord('M') + part.count('/')) * 3 if part not in constants.PREDEFINED_TYPE_DICT else
                         constants.PREDEFINED_TYPE_DICT[part])

            i = j + 1
        return parts

    def normlize_method(self, mline):
        parts = []

        modifiers = mline[:mline.rfind(' ')].split(' ')
        for modifier in modifiers:
            if modifier in constants.MODIFIER_DICT:
                parts.append(constants.MODIFIER_DICT[modifier])

        m_name_type = mline[mline.rfind(' ') + 1:]
        if '(' not in m_name_type or ')' not in m_name_type:
            return modifier

        params = m_name_type[m_name_type.find('(') + 1:m_name_type.rfind(')')]
        parts.extend(self.normlize_types(params))

        ret = m_name_type[m_name_type.rfind(')') + 1:]
        parts.extend(self.normlize_types(ret))

        return ''.join(parts)

    def normlize_invoke(self, iline):
        parts = []
        cname = iline[:iline.find('->')]
        cname = chr(ord('M') + cname.count('/')) * 3 if cname not in constants.PREDEFINED_TYPE_DICT else \
        constants.PREDEFINED_TYPE_DICT[cname]
        parts.append(cname)

        m_name_type = iline[iline.find('->') + len('->'):]
        if '(' not in m_name_type or ')' not in m_name_type:
            return ''.join(parts)

        params = m_name_type[m_name_type.find('(') + 1:m_name_type.rfind(')')]
        parts.extend(self.normlize_types(params))

        ret = m_name_type[m_name_type.rfind(')') + 1:]
        parts.extend(self.normlize_types(ret))

        return ''.join(parts)

    def normlize_field(self, fline):
        parts = []
        if ' = ' in fline:
            f_value = fline[fline.find(' = ') + 1:]
            parts.append(f_value)
            fline = fline[:fline.find(' = ')]

        modifiers = fline[:fline.rfind(' ')].split(' ')
        for modifier in modifiers:
            if modifier in constants.MODIFIER_DICT:
                parts.append(constants.MODIFIER_DICT[modifier])

        f_name_type = fline[fline.rfind(' ') + 1:]
        if ':' not in f_name_type:
            return ''.join(parts)

        f_type = f_name_type[f_name_type.find(':') + 1:]
        parts.extend(self.normlize_types(f_type))

        return ''.join(parts)

    def parse_smali(self, module_name, smali_full_path, smali_relative_path):
        constants = set([])

        with open(smali_full_path, 'r') as sfile:
            lines = sfile.readlines()
            for line in lines:
                line = line.strip()

                if 'const-string' in line:
                    cstr = line[line.find('"') + 1:line.rfind('"')]
                    constants.add(cstr[:32])  # we don't expect super long strings here.

                if line.startswith('.super '):
                    tps = self.normlize_types(line[line.find('.super ') + len('.super '):])
                    constants.add('K%s' % ''.join(tps))

                if line.startswith('.implements '):
                    tps = self.normlize_types(line[line.find('.implements ') + len('.implements '):])
                    constants.add('L%s' % ''.join(tps))

                if line.startswith('.method '):
                    cstr = self.normlize_method(line[line.find('.method ') + len('.method '):])
                    constants.add(cstr)

                if line.startswith('.field '):
                    cstr = self.normlize_field(line[line.find('.field ') + len('.field '):])
                    constants.add(cstr)

                if line.startswith('invoke-'):
                    cstr = self.normlize_invoke(line[line.find('}, ') + len('}, '):])
                    constants.add(cstr)

        fingerprint = ''.join(sorted(list(constants)))
        self.module_fingerprints[module_name][smali_relative_path] = fingerprint

    def dump_fingerprints(self):
        for module_name, fingerprints in self.module_fingerprints.items():
            print('module: %s' % module_name)
            for _, fingerprint in fingerprints.items():
                print('\t fingerprint: %s' % fingerprint)
