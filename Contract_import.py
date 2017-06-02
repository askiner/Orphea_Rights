# coding: utf-8

from os import path as os_path, remove as os_remove, mkdir, listdir
from shutil import copyfile
from subprocess import call
import ntpath
import time
from image_description import ImageDescription

# mac config
locations = {
    'source': r'/Users/Shared/test/test1',
    'backup': r'/Users/Shared/test/test-backup',
    'import': r'/Users/Shared/test/test-import',
    'xml' : r'/Users/Shared/test/test-xml',
    'reuse_xml': r'/Users/Shared/test/test-reuse'
}

# pc config
#locations = {
#    'source': r'\\WS01364341.corp.tass.ru\_',
#    'backup': r'C:\backup\Contract_folder',
#    'import': r'\\ftp.tass.ru\FTP\Photo\assets\TASS\reserve\Редакция сайта tass.ru'
#}

extentions = {
    'image': ['jpg', 'jpeg'],
    'meta': 'xml',
    'processing': ['jpg', 'jpeg', 'xml']
}

do_backup = True
reuse_xml = True


def write_fixture(file, guid):
    if os_path.exists(file):
        cmd_line = 'exiftool "{}" -m -overwrite_original -IPTC:FixtureIdentifier="{}"'.format(file, guid)
        call(cmd_line)


def is_check_paths(loc):
    for key in loc.keys():
        if not os_path.exists(loc[key]):
            print("Folder {} is wrong: {}! Stop processing...".format(key, loc[key]))
            return False
    return True


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def find_with_extention(path, name, extention):
    if os_path.exists(os_path.join(path, "{}.{}".format(name, extention))):
        return {'filename': "{}.{}".format(name, extention), 'name': name, 'extention': extention}
    else:
        return None


def main(loc):
    # search all pairs if no XML - ignore
    build_pairs = {}

    for file in listdir(loc['source']):
        input_package = {}
        filename_part, extention = file.split('.')

        if filename_part not in build_pairs.keys():
            if extention.lower() in ['jpg', 'jpeg']:
                input_package['image'] = {'filename': file, 'name': filename_part, 'extention': extention.lower()}
                result = find_with_extention(loc['source'], filename_part, 'xml')
                if result:
                    input_package['meta'] = result
            if extention.lower() in ['xml']:
                input_package['meta'] = {'filename': "{}.xml".format(filename_part), 'name': filename_part, 'extention': 'xml'}
                result = find_with_extention(loc['source'], filename_part, 'jpg')
                if result:
                    input_package['image'] = result
                else:
                    result = find_with_extention(loc['source'], filename_part, 'jpeg')
                    if result:
                        input_package['image'] = result

            if 'image' in input_package.keys() and input_package['image'] and 'meta' in input_package.keys() and input_package['meta']:
                build_pairs[filename_part] = input_package

    for file_item in build_pairs.keys():
        try:
            process(loc, build_pairs[file_item])
        except:
            continue


def process(location, file):
    if 'meta' in file.keys():
        desc = ImageDescription(os_path.join(location['source'], file['meta']['filename']), file['image']['filename'])
        if desc.IsReady:

            if do_backup:
                if os_path.exists(location['backup']):
                    day_backup_path = os_path.join(location['backup'], time.strftime('%Y-%m-%d'))
                    if not os_path.exists(day_backup_path):
                        mkdir(os_path.join(day_backup_path))

                    for item in file.keys():
                        if os_path.exists(os_path.join(location['source'], file[item]['filename'])):
                            copyfile(os_path.join(location['source'], file[item]['filename']),
                                     os_path.join(day_backup_path, file[item]['filename']))

            desc.save_xml(location['xml'])

            copyfile(os_path.join(location['source'], file['image']['filename']),
                     os_path.join(location['import'], "{}_{}".format(desc.ContractId, file['image']['filename'])))

            if reuse_xml:
                copyfile(os_path.join(location['source'], file['meta']['filename']),
                         os_path.join(location['reuse_xml'], file['meta']['filename']))

            os_remove(os_path.join(location['source'], file['image']['filename']))
            os_remove(os_path.join(location['source'], file['meta']['filename']))


if __name__ == "__main__":
    if is_check_paths(locations):
        main(locations)