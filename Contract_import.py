# coding: utf-8

"""TODO: get date of contract
TODO: set dates to photos
TODO: set dates to reportage
TODO: set reportage name"""

from os import path as os_path, remove as os_remove, mkdir, listdir
from shutil import copyfile
from subprocess import call, Popen, PIPE
import ntpath
import time
import urllib.error # исключение, для получения ситуаций с недоступностью сервиса или изменения его формата
from json import (loads as jsLoads, dumps as jsDumps)
from urllib.parse import quote  # кодирование символов (аналог urlencode)
from urllib.request import Request as HttpRequest, urlopen as UrlOpen
from image_description import ContentDescription
import time  # to set delay between updates
import datetime
import dateutil.parser

# mac config
#locations = {
#    'source': r'/Users/Shared/test/test1',
#    'backup': r'/Users/Shared/test/test-backup',
#    'import': r'/Users/Shared/test/test-import',
#    'xml': r'/Users/Shared/test/test-xml',
#    'reuse_xml': r'/Users/Shared/test/test-reuse'
#}

DELAY = .5  # seconds before next file send

# pc config
locations = {
    'source': [r'\\ftp.tass.ru\FTP\Photo\assets\Partners\Contracts\tassru', r'\\corp.tass.ru\TASS_files\Фото\Контракты'],
    'backup': r'C:\backup\contracts',
    #'import': r'C:\temp\test_import',
    'import': r'\\ftp.tass.ru\FTP\Photo\assets\TASS\Contracts',
    #'xml': r'C:\temp\test-xml',
    'xml': r'\\ftp.tass.ru\FTP\Photo\assets\Partners\UPDATE\XML\xml_contracts',
    'reuse_xml': r'C:\backup\contracts_reuse-xml',
    'duplicates': r'C:\backup\contracts_duplicates',
    'exiftool': r'C:\Apps\exiftool.exe'
}

ignore_folders = ['xml-update']

good_formats = {
    'image': {'ext': ['jpg', 'jpeg', 'png'], 'folder': 'image'},
    'video': {'ext': ['mpg', 'avi', 'qtw', 'gt', 'mp4', 'mts', 'mov'], 'folder': 'video'},
    'graphics': {'ext': ['pdf', 'ai'], 'folder': 'graphics'},
    'audio': {'ext': ['wav', 'mp3', 'ram'], 'folder': 'audio'},
    'meta': {'ext': 'xml', 'folder': 'image'}
    # 'processing': ['jpg', 'jpeg', 'xml']
}

service_url = 'http://msk-oft-app01:8080/photos/byfilename/{0}'

do_backup = False
reuse_xml = True


def check_file_existence(filename):
    try:
        photo_object = get_photo_by_url(service_url.format(quote(filename)))
        if photo_object is not None and 'Id' in photo_object and int(photo_object['Id']) > 0:
            return True
        else:
            return False
    except:
        return False

# def write_fixture(file, guid):
#    if os_path.exists(file):
#        cmd_line = 'exiftool "{}" -m -overwrite_original -IPTC:FixtureIdentifier="{}"'.format(file, guid)
#        call(cmd_line)

def get_create_date(file):
    """Получение даты файла, если эта дата не получена из 1С. Приоритет: IPTC:DateCreated, EXIF:DateTimeOriginal, SystemDate"""
    if os_path.exists(file):
        result_date = None
        metadata = get_metadata(file)
        if metadata is not None:
            if 'IPTC_DateCreated' in metadata.keys() and metadata['IPTC_DateCreated'] is not None:
                result_date = metadata['IPTC_DateCreated']
            else:
                if 'EXIF_DateTimeOriginal' in metadata.keys() and metadata['EXIF_DateTimeOriginal'] is not None:
                    result_date = metadata['EXIF_DateTimeOriginal']

        if result_date is None:
            return datetime.datetime.now()
        else:
            return result_date


def get_metadata(path_to_file):

    if os_path.exists(path_to_file):

        command = Popen([locations['exiftool'],
                         path_to_file,
                         '-IPTC:DateCreated',
                         '-EXIF:DateTimeOriginal',
                         '-j'],
                        stdin=PIPE,
                        stdout=PIPE,
                        stderr=PIPE)

        output, err = command.communicate()

        if output:
            data = jsLoads(output.decode('utf-8'))

            itpc_DateCreated = None
            exif_DateTimeOriginal = None

            if 'DateCreated' in data[0] and data[0]['DateCreated'] and len(str(data[0]['DateCreated'])) > 0:
                print(data[0]['DateCreated'])
                itpc_DateCreated = dateutil.parser.parse(str(data[0]['DateCreated']).replace(":", "-"), default=dateutil.parser.parse("00:00:00Z"))
                print(itpc_DateCreated)

            if 'DateTimeOriginal' in data[0] and data[0]['DateTimeOriginal'] and len(str(data[0]['DateTimeOriginal'])) > 0:
                exif_DateTimeOriginal = dateutil.parser.parse(data[0]['DateTimeOriginal'])

            return {'IPTC_DateCreated': itpc_DateCreated, 'EXIF_DateTimeOriginal': exif_DateTimeOriginal }

        else:
            return None


def get_photo_by_url(url):
    """ Соединение с сервисом tassphoto.com и получение информации об уже добавленной фото
    :param url: ссылка для получения информации о фото
    :return: объект с информацией о фото на сайте
    """
    try:
        with UrlOpen(url) as service_response:
            if service_response is not None:
                photos = jsLoads(service_response.read().decode('utf-8'))

                if 'data' in photos and photos['data']:
                    if isinstance(photos['data'], list):
                        return photos['data'](1)
                    elif isinstance(photos['data'], dict):
                        return photos['data']
                    else:
                        raise ValueError("Wrong object in response: {}".format(str(photos['data'])))
                else:
                    return None

    except urllib.error.HTTPError as http_error:
        raise(SystemError("Request error, code: {}, message: {}".format(http_error.code, http_error.msg)))


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
        # build_pairs = get_pairs_from_path(source_path)
        build_pairs = get_pairs(source_path)
        for file_item in build_pairs.keys():
            # try:
            process(loc, build_pairs[file_item])
            time.sleep(DELAY)  # sleep 5 seconds
            # except:
            #     continue


def get_pairs(path):
    build_pairs = {}

    for fs_item in listdir(path):

        # if folder is in ignore list - proceed to next
        if fs_item in ignore_folders:
            continue

        fs_item_path = os_path.join(path, fs_item)
        if os_path.isdir(fs_item_path):
            build_pairs.update(get_pairs_from_path(fs_item_path))

    # do it for files
    build_pairs.update(get_pairs_from_path(path))

    return build_pairs


def get_pairs_from_path(path):
    build_pairs = {}
    for file in listdir(path):

        input_package = {}

        if os_path.isdir(os_path.join(path, file)):
            continue

        filename_part, extension = file.rsplit('.', maxsplit=1)
        print(filename_part)

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
        print("Processing: {}".format(file[content_type]['filename']))

        desc = ContentDescription(file['meta']['filepath'], file[content_type]['filename'])

        if desc.CreationDate is None:
            desc.CreationDate = get_create_date(file[content_type]['filepath'])

        if desc.is_ready() and os_path.exists(os_path.join(location['import'], desc.Publishing)):

            if check_file_existence(desc.get_filename()):

                # copyfile(os_path.join(location['source'], file[content_type]['filename']),
                copyfile(file[content_type]['filepath'],
                         os_path.join(location['duplicates'], desc.get_filename()))

                if not os_path.exists(os_path.join(location['duplicates'], 'xml')):
                    mkdir(os_path.join(location['duplicates'], 'xml'))
                desc.save_xml(os_path.join(location['duplicates'], 'xml'))

            else:

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
    print(datetime.datetime.now())
    if is_check_paths(locations):
        main(locations)
