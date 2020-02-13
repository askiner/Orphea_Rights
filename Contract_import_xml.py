# coding: utf-8

from os import path as os_path, remove as os_remove, mkdir, listdir
from shutil import copyfile, move
from subprocess import call
import ntpath
import time
from image_description import ContentDescription

# pc config
locations = {
    'source_update': r'\\corp.tass.ru\TASS_Files\Фото\Контракты\update',
    #'source_update': r'\\corp.tass.ru\TASS_Files\Фото\Контракты\update-test',
    # 'source_delete': r'\\corp.tass.ru\TASS_Files\Фото\Контракты\delete', # TODO: Add update of this
    'backup': r'\\corp.tass.ru\TASS_Files\Фото\Контракты\backup',
    'error': r'\\corp.tass.ru\TASS_Files\Фото\Контракты\errors',
    # 'import': r'\\ftp.tass.ru\FTP\Photo\assets\TASS\reserve\Редакция сайта tass.ru',
    'xml': r'\\corp.tass.ru\TASS_Files\FTP\Photo\assets\TASS\xml'
    #'xml': r'\\corp.tass.ru\TASS_Files\Фото\Контракты\update-test\result'
}

do_backup = True
reuse_xml = True


def is_check_paths(loc):
    for key in loc.keys():
        if not os_path.exists(loc[key]):
            print("Folder {} is wrong: {}! Stop processing...".format(key, loc[key]))
            return False
    return True


def main(loc):
    # search all pairs if no XML - ignore
    tasks = {}

    for file in listdir(loc['source_update']):
        input_package = {}
        if '.' in file:
            filename_part, extension = file.split('.')

            if filename_part not in tasks.keys():

                # if extension.lower() in good_formats['meta']['ext']:
                if extension.lower() == 'xml':
                    input_package['meta'] = {'filename': file, 'name': filename_part, 'extension': extension.lower(), 'path': os_path.join(loc['source_update'], file)}
                    input_package['operation'] = 'update'

                if 'meta' in input_package.keys() and input_package['meta']:
                    tasks[filename_part] = input_package

    for task_item in tasks.keys():
        try:
            process(loc, tasks[task_item])
        except:
            continue


def process(location, file):

    if 'meta' in file.keys():
        desc = ContentDescription(file['meta']['path'], None)

        print(file['meta']['filename'])

        if desc.isError:
            if os_path.exists(location['error']):
                try:
                    move(file['meta']['path'], os_path.join(location['error'], file['meta']['filename']))
                    print(' - ERROR!\n')
                except:
                    return
            return

        if do_backup:
            if os_path.exists(location['backup']):
                day_backup_path = os_path.join(location['backup'], time.strftime('%Y-%m-%d'))
                if not os_path.exists(day_backup_path):
                    mkdir(os_path.join(day_backup_path))

                if os_path.exists(file['meta']['path']):
                    copyfile(file['meta']['path'], os_path.join(day_backup_path, file['meta']['filename']))

        desc.save_xml_2(location['xml'])

        os_remove(file['meta']['path'])
        print(' - ok\n')


if __name__ == "__main__":
    if is_check_paths(locations):
        main(locations)
