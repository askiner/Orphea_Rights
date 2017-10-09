# coding: utf-8

"""TODO: get date of contract
TODO: set dates to photos
TODO: set dates to reportage
TODO: set reportage name"""

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
    'source': [r'\\ftp.tass.ru\FTP\Photo\assets\Partners\Contracts\tassru', r'S:\Фото\Контракты'],
    'backup': r'C:\temp\test_backup',
    #'import': r'C:\temp\test_import',
    'import': r'\\ftp.tass.ru\FTP\Photo\assets\TASS\Contracts',
    #'xml': r'C:\temp\test-xml',
    'xml': r'\\ftp.tass.ru\FTP\Photo\assets\Partners\UPDATE\XML\xml_contracts',
    'reuse_xml': r'C:\temp\reuse-xml'
}

good_formats = {
    'image': {'ext': ['jpg', 'jpeg', 'png'], 'folder': 'image'},
    'video': {'ext': ['mpg', 'avi', 'qtw', 'gt', 'mp4', 'mts', 'mov'], 'folder': 'video'},
    'graphics': {'ext': ['pdf', 'ai'], 'folder': 'graphics'},
    'audio': {'ext': ['wav', 'mp3', 'ram'], 'folder': 'audio'},
    'meta': {'ext': 'xml', 'folder': 'image'}
    # 'processing': ['jpg', 'jpeg', 'xml']
}

do_backup = True
reuse_xml = True


# def write_fixture(file, guid):
#    if os_path.exists(file):
#        cmd_line = 'exiftool "{}" -m -overwrite_original -IPTC:FixtureIdentifier="{}"'.format(file, guid)
#        call(cmd_line)


def is_check_paths(loc):
    for key in loc.keys():
        if isinstance(loc[key], list):
            for pt in loc[key]:
                if not os_path.exists(pt):
                    print("Folder {} is wrong! Stop processing...".format(pt))
                    return False
        else:
            if not os_path.exists(loc[key]):
                print("Folder {} is wrong: {}! Stop processing...".format(key, loc[key]))
                return False
    return True


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def find_with_extension(path, name, extension):
    if os_path.exists(os_path.join(path, "{}.{}".format(name, extension))):
        return {'filename': "{}.{}".format(name, extension), 'name': name, 'extension': extension,
                'filepath': os_path.join(path, "{}.{}".format(name, extension))}
    else:
        return None


def main(loc):
    for source_path in loc['source']:
        build_pairs = get_pairs_from_path(source_path)
        for file_item in build_pairs.keys():
            try:
                process(loc, build_pairs[file_item])
            except:
                continue


def get_pairs_from_path(path):
    build_pairs = {}
    for file in listdir(path):
        input_package = {}

        if os_path.isdir(os_path.join(path, file)):
            continue

        filename_part, extension = file.split('.')

        if filename_part not in build_pairs.keys():
            if extension.lower() in good_formats['image']['ext']:
                input_package['image'] = {'filename': file, 'name': filename_part, 'extension': extension.lower(),
                                          'filepath': os_path.join(path, file)}
                result = find_with_extension(path, filename_part, 'xml')
                if result:
                    input_package['meta'] = result

            if extension.lower() in good_formats['audio']['ext']:
                input_package['audio'] = {'filename': file, 'name': filename_part, 'extension': extension.lower(),
                                          'filepath': os_path.join(path, file)}
                result = find_with_extension(path, filename_part, 'xml')
                if result:
                    input_package['meta'] = result

            if extension.lower() in good_formats['video']['ext']:
                input_package['video'] = {'filename': file, 'name': filename_part, 'extension': extension.lower(),
                                          'filepath': os_path.join(path, file)}
                result = find_with_extension(path, filename_part, 'xml')
                if result:
                    input_package['meta'] = result

            if extension.lower() in good_formats['graphics']['ext']:
                input_package['graphics'] = {'filename': file, 'name': filename_part, 'extension': extension.lower(),
                                             'filepath': os_path.join(path, file)}
                result = find_with_extension(path, filename_part, 'xml')
                if result:
                    input_package['meta'] = result

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

            if (('image' in input_package.keys() and input_package['image'])
                or ('audio' in input_package.keys() and input_package['audio'])
                or ('video' in input_package.keys() and input_package['video'])
                or ('graphics' in input_package.keys() and input_package['graphics'])) \
                    and 'meta' in input_package.keys() and input_package['meta']:
                build_pairs[filename_part] = input_package
    return build_pairs


def process(location, file):

    content_type = None

    if 'image' in file.keys() and file['image'] is not None:
        content_type = 'image'
    else:
        if 'video' in file.keys() and file['video'] is not None:
            content_type = 'video'
        else:
            if 'graphics' in file.keys() and file['graphics'] is not None:
                content_type = 'graphics'
            else:
                if 'audio' in file.keys() and file['audio'] is not None:
                    content_type = 'audio'

    if 'meta' in file.keys() and content_type is not None:
        # desc = ContentDescription(os_path.join(location['source'], file['meta']['filename']), file[content_type]['filename'])
        desc = ContentDescription(file['meta']['filepath'], file[content_type]['filename'])
        if desc.IsReady and os_path.exists(os_path.join(location['import'], desc.Publishing)):

            if do_backup:
                if os_path.exists(location['backup']):
                    day_backup_path = os_path.join(location['backup'], time.strftime('%Y-%m-%d'))
                    if not os_path.exists(day_backup_path):
                        mkdir(os_path.join(day_backup_path))

                    for item in file.keys():
                        # if os_path.exists(os_path.join(location['source'], file[item]['filename'])):
                        if os_path.exists(file[item]['filepath']):
                            # copyfile(os_path.join(location['source'], file[item]['filename']),
                            copyfile(file[item]['filepath'], os_path.join(day_backup_path, file[item]['filename']))

            desc.save_xml(location['xml'])

            # copy to reportage
            if not os_path.exists(os_path.join(location['import'], desc.Publishing, "reportages", content_type)):
                mkdir(os_path.join(location['import'], desc.Publishing, "reportages", content_type))

            # copyfile(os_path.join(location['source'], file[content_type]['filename']),
            copyfile(file[content_type]['filepath'],
                     os_path.join(location['import'], desc.Publishing, "reportages", content_type, desc.get_filename()))

            if reuse_xml:
                # copyfile(os_path.join(location['source'], file['meta']['filename']),
                copyfile(file['meta']['filepath'],
                         os_path.join(location['reuse_xml'], file['meta']['filename']))

            # os_remove(os_path.join(location['source'], file[content_type]['filename']))
            os_remove(file[content_type]['filepath'])
            # os_remove(os_path.join(location['source'], file['meta']['filename']))
            os_remove(file['meta']['filepath'])


if __name__ == "__main__":
    if is_check_paths(locations):
        main(locations)
