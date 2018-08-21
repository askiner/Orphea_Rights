# coding: utf-8

from os import path as os_path, remove as os_remove, mkdir, listdir
from shutil import copyfile
from subprocess import call
import ntpath
import time
from image_description import ContentDescription

# mac config
#locations = {
#    'source': r'/Users/Shared/test/test1',
#    'backup': r'/Users/Shared/test/test-backup',
#    'import': r'/Users/Shared/test/test-import',
#    'xml': r'/Users/Shared/test/test-xml',
#    'reuse_xml': r'/Users/Shared/test/test-reuse'
#}

# pc config
locations = {
    'source_update': r'S:\Фото\Контракты\update',
    'source_delete': r'S:\Фото\Контракты\delete',
    'backup': r'C:\backup\Contract_folder',
    # 'import': r'\\ftp.tass.ru\FTP\Photo\assets\TASS\reserve\Редакция сайта tass.ru',
    'xml': r'S:\FTP\Photo\assets\TASS\xml'
}

# good_formats = {
#    'image': {'ext': ['jpg', 'jpeg'], 'folder': 'image'},
#    'video': {'ext': ['mpg', 'avi', 'qtw', 'gt', 'mp4', 'mts', 'mov'], 'folder': 'video'},
#    'graphics': {'ext': ['pdf', 'ai'], 'folder': 'graphics'},
#    'audio': {'ext': ['wav', 'mp3', 'ram'], 'folder': 'audio'},
#    'meta': {'ext': 'xml', 'folder': 'image'}
    # 'processing': ['jpg', 'jpeg', 'xml']
#}

do_backup = True
reuse_xml = True


# def write_fixture(file, guid):
#    if os_path.exists(file):
#        cmd_line = 'exiftool "{}" -m -overwrite_original -IPTC:FixtureIdentifier="{}"'.format(file, guid)
#        call(cmd_line)


def is_check_paths(loc):
    for key in loc.keys():
        if not os_path.exists(loc[key]):
            print("Folder {} is wrong: {}! Stop processing...".format(key, loc[key]))
            return False
    return True


# def path_leaf(path):
#    head, tail = ntpath.split(path)
#    return tail or ntpath.basename(head)


# def find_with_extension(path, name, extension):
#    if os_path.exists(os_path.join(path, "{}.{}".format(name, extension))):
#        return {'filename': "{}.{}".format(name, extension), 'name': name, 'extension': extension}
#    else:
#        return None


def main(loc):
    # search all pairs if no XML - ignore
    tasks = {}

    for file in listdir(loc['source_update']):
        input_package = {}
        filename_part, extension = file.split('.')

        if filename_part not in tasks.keys():

            # if extension.lower() in good_formats['meta']['ext']:
            if extension.lower() == 'xml':
                input_package['meta'] = {'filename': file, 'name': filename_part, 'extension': extension.lower(), 'path': os_path.join(loc['source_update'], file)}
                input_package['operation'] = 'update'

            # if extension.lower() in ['xml']:
            #    input_package['meta'] = {'filename': "{}.xml".format(filename_part),
            #                             'name': filename_part,
            #                             'extension': 'xml'}
            #    result = find_with_extension(loc['source'], filename_part, 'jpg')
            #    if result:
            #        input_package['image'] = result
            #    else:
            #        result = find_with_extention(loc['source'], filename_part, 'jpeg')
            #       if result:
            #            input_package['image'] = result

            if 'meta' in input_package.keys() and input_package['meta']:
                tasks[filename_part] = input_package

    for task_item in tasks.keys():
        try:
            process(loc, tasks[task_item])
        except:
            continue


def process(location, file):

    # content_type = None

#    if 'image' in file.keys() and file['image'] is not None:
#        content_type = 'image'
#    else:
#        if 'video' in file.keys() and file['video'] is not None:
#            content_type = 'video'
#        else:
#            if 'graphics' in file.keys() and file['graphics'] is not None:
#                content_type = 'graphics'
#            else:
#                if 'audio' in file.keys() and file['audio'] is not None:
#                    content_type = 'audio'

    #if 'meta' in file.keys() and content_type is not None:
    if 'meta' in file.keys():
        desc = ContentDescription(file['meta']['path'], None)

        if do_backup:
            if os_path.exists(location['backup']):
                day_backup_path = os_path.join(location['backup'], time.strftime('%Y-%m-%d'))
                if not os_path.exists(day_backup_path):
                    mkdir(os_path.join(day_backup_path))

                if os_path.exists(file['meta']['path']):
                    copyfile(file['meta']['path'], os_path.join(day_backup_path, file['meta']['filename']))

        desc.save_xml_2(location['xml'])

        # copyfile(os_path.join(location['source'], file[content_type]['filename']),
        # os_path.join(location['import'], desc.Publishing, content_type, "{}_{}_{}".format(desc.ContractId, desc.FixedIdentifier, file[content_type]['filename'])))

        # if reuse_xml:
        #     copyfile(os_path.join(location['source'], file['meta']['filename']),
        #              os_path.join(location['reuse_xml'], file['meta']['filename']))

        # os_remove(os_path.join(location['source'], file[content_type]['filename']))
        os_remove(file['meta']['path'])



if __name__ == "__main__":
    if is_check_paths(locations):
        main(locations)
