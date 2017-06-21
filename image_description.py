# coding: utf-8

from os import path as os_path, remove as os_remove, mkdir, listdir
from xml.etree import cElementTree as et
import dateutil.parser


class ContentDescription:
    FixedIdentifier = None
    Caption = None
    CreationDate = None
    Contract = None
    ContractId = None
    License = None
    LicenseStartDate = None
    LicenseEndDate = None
    Publishing = None
    Title = None
    OriginalName = None

    IsReady = True

    Limits = {
        'Title': 120,
        'Caption': 2000
    }

    def __init__(self, file_path, orig_name):
        self.OriginalName = orig_name
        self.read_xml(file_path)

    def read_xml(self, file_path):
        if os_path.exists(file_path):
            self.IsReady = True
            root = et.parse(file_path).getroot()

            if root.find('fixident') is not None:
                self.FixedIdentifier = root.find('fixident').text
            else:
                self.IsReady = False

            if root.find('captionweb') is not None:
                self.Caption = root.find('captionweb').text

            if root.find('title') is not None:
                t_title = root.find('title').text
                if len(t_title) > self.Limits['Title']:
                    self.Title = t_title[:self.Limits['Title']]
                else:
                    self.Title = t_title
            else:
                if self.Caption is not None:
                    if len(self.Caption) > self.Limits['Title']:
                        self.Title = self.Caption[:self.Limits['Title']]
                    else:
                        self.Title = self.Caption

            if root.find('creationdate') is not None:
                self.CreationDate = dateutil.parser.parse(root.find('creationdate').text)
            else:
                self.IsReady = False

            if root.find('contract') is not None:
                self.Contract = root.find('contract').text
            else:
                self.IsReady = False

            if root.find('contract_id') is not None:
                self.ContractId = root.find('contract_id').text
            else:
                self.IsReady = False

            if root.find('license') is not None:
                self.License = root.find('license').text

            if root.find('lincese_start') is not None:
                self.LicenseStartDate = dateutil.parser.parse(root.find('lincese_start').text)

            if root.find('lincese_expire') is not None:
                self.LicenseEndDate = dateutil.parser.parse(root.find('lincese_expire').text)

            if root.find('publishing') is not None:
                self.Publishing = root.find('publishing').text
            else:
                self.IsReady = False

    def save_xml(self, path):
        """
        Creates and serilizes XML for Orphea
        :return: None
        """

        if not path:
            raise ValueError('path is not set!')

        filename = None

        if not self.IsReady:
            raise ValueError('Data is not ready!')

        root = et.Element("assets")

        if self.FixedIdentifier is not None:
            et.SubElement(root, "fixident").text = self.FixedIdentifier
            filename = os_path.join(path, "{}.xml".format(self.FixedIdentifier))

        if self.Title:
            et.SubElement(root, "title").text = self.Title

        if self.Caption:
            new_caption = self.SetNewCaption()
            et.SubElement(root, "captionweb").text = new_caption
            et.SubElement(root, "subtitle").text = new_caption
            et.SubElement(root, "caption").text = new_caption

        if self.CreationDate:
            et.SubElement(root, "creationdate").text = self.CreationDate.strftime("%d.%m.%Y")

        if filename:
            tree = et.ElementTree(root)
            tree.write(filename, encoding='utf-8', xml_declaration=True)

    def SetNewCaption(self):
        """Update caption with licence info
        :return: new caption with additions
        """
        caption = self.Caption
        if self.Contract is not None:
            caption = u'{}\nДоговор: {}'.format(caption, self.Contract)

        if self.ContractId is not None:
            caption = u'{}\nДоговор ID: {}'.format(caption, self.ContractId)

        if self.License is not None:
            caption = u'{}\nЛицензия: {}'.format(caption, self.License)

        if self.LicenseStartDate is not None or self.LicenseEndDate is not None:
            caption = u'{}\nСрок лицензии:'.format(caption)
            if self.LicenseStartDate is not None:
                caption = u'{} с {}'.format(caption, self.LicenseStartDate.strftime("%d.%m.%Y"))

            if self.LicenseEndDate is not None:
                caption = u'{} по {}'.format(caption, self.LicenseEndDate.strftime("%d.%m.%Y"))

        if self.Publishing is not None:
            caption = u'{}\nРедакция: {}'.format(caption, self.Publishing)

        if self.OriginalName is not None:
            caption = u'{}\nИмя файла: {}'.format(caption, self.OriginalName)

        return caption