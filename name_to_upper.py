from os import path as os_path, listdir
from xml.etree import cElementTree as et


def main(pth):
    if pth and os_path.exists(pth):
        for file in listdir(pth):
            tree = et.parse(os_path.join(pth, file))

            if tree.find('original_filename') is not None and tree.find('original_filename').text:
                tree.find('original_filename').text = tree.find('original_filename').text.upper()
                tree.write(os_path.join(pth, file), encoding='utf-8', xml_declaration=True)


if __name__ == "__main__":
    main(r'C:\temp\xml_in')