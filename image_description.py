# coding: utf-8

from os import path as os_path, remove as os_remove, mkdir, listdir
from xml.etree import cElementTree as et
import dateutil.parser
from transliterate import translit  # , get_available_language_codes
import datetime


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
    Credit = None
    Byline = None
    Sublicense = None
    Id = None
    Author = None               # Real name of the author (or whome rights are belongs)

    Type_of_use = None          # What type of use is allowed
    Territory = None            # Where are the use of the photo is allowed

    # IsReady = True

    Limits = {
        'Title': 120,
        'Caption': 2000
    }

    def __init__(self, file_path, orig_name):
        # self.OriginalName = orig_name
        self.read_xml(file_path)

        if orig_name is not None:
            self.OriginalName = orig_name

    def is_ready(self):
        return self.FixedIdentifier is not None and self.CreationDate is not None and self.Contract is not None and self.ContractId is not None and self.Publishing is not None

    def read_xml(self, file_path):
        if os_path.exists(file_path):
            # self.IsReady = True
            root = et.parse(file_path).getroot()

            if root.find('id_objet') is not None:
                self.Id = root.find('id_objet').text

            if root.find('fixident') is not None:
                self.FixedIdentifier = root.find('fixident').text
            # else:
            #    self.IsReady = False

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
                    self.Title = self.Caption
                    if len(self.Caption) > (self.Limits['Title']):
                        self.Title = self.Caption[:self.Limits['Title']]
                    # else:
                    #     self.Title = self.Caption
                else:
                    if self.Contract is not None:
                        self.Title = self.Contract

            if root.find('creationdate') is not None:
                if root.find('creationdate').text is not None and len(root.find('creationdate').text) > 0:
                    self.CreationDate = dateutil.parser.parse(root.find('creationdate').text)
                else:
                    # self.CreationDate = datetime.datetime.now()
                    self.CreationDate = None
            # else:
            #    self.IsReady = False

            if root.find('contract') is not None:
                self.Contract = root.find('contract').text
            # else:
            #    self.IsReady = False

            if root.find('contract_id') is not None:
                self.ContractId = root.find('contract_id').text
            # else:
            #    self.IsReady = False

            if root.find('license') is not None:
                self.License = root.find('license').text

            if root.find('Sublicense') is not None:
                self.Sublicense = root.find('Sublicense').text

            if root.find('sublicense') is not None:
                self.Sublicense = root.find('sublicense').text

            if root.find('lincese_start') is not None and root.find('lincese_start').text is not None:
                self.LicenseStartDate = dateutil.parser.parse(root.find('lincese_start').text)

            if root.find('lincese_expire') is not None and root.find('lincese_expire').text is not None:
                self.LicenseEndDate = dateutil.parser.parse(root.find('lincese_expire').text)

            if root.find('publishing') is not None:
                self.Publishing = root.find('publishing').text
            # else:
            #    self.IsReady = False

            if root.find('byline') is not None:
                self.Byline = root.find('byline').text

            if root.find('Byline') is not None:
                self.Byline = root.find('Byline').text

            if root.find('credit') is not None:
                self.Credit = root.find('credit').text

            if root.find('territory') is not None:
                self.Territory = root.find('territory').text

            if root.find('Territory') is not None:
                self.Territory = root.find('Territory').text

            if root.find('typeofuse') is not None:
                self.Type_of_use = root.find('typeofuse').text

            if root.find('author') is not None:
                self.Author = root.find('author').text

            if root.find('filename') is not None:
                self.OriginalName = root.find('filename').text

    def clean_for_path_use(self, value):
        return value.replace('?', '')\
            .replace('*', ' ')\
            .replace('_', ' ')\
            .replace('\'', '')

    def get_filename(self):

        filename = ''
        # if self.ContractId is not None:
        #     filename = "{}".format(self.ContractId)

        #if self.Contract is not None:
        if self.ContractId is not None:
            filename = "{}".format(self.ContractId)
            #filename = "{}".format(translit(self.Contract, 'ru', reversed=True)
            #                       .replace('?', '')
            #                       .replace('*', '-')
            #                       .replace('_', '-')
            #                       .replace('\'', '')
            #                       .replace('\\', '-')
            #                       .replace('/', '-')
            #                       .replace('№', '-'))
        else:
            if self.Byline is not None:
                filename = "{}".format(self.clean_for_path_use(translit(self.Byline, 'ru', reversed=True)))
            else:
                if self.Author is not None:
                    filename = "{}".format(self.clean_for_path_use(translit(self.Author, 'ru', reversed=True)))

        if self.FixedIdentifier is not None:
            filename = "{}_{}".format(filename, self.FixedIdentifier)

        if self.OriginalName is not None:
            filename_part, extension = self.OriginalName.rsplit('.', maxsplit=1)
            filename = "{}.{}".format(filename, extension)
            # filename = "{}_{}".format(filename, translit(self.OriginalName, 'ru', reversed=True))

        #if self.ContractId is not None and self.FixedIdentifier is not None and self.OriginalName is not None:
        #   return "{}_{}_{}".format(self.ContractId, self.FixedIdentifier, self.OriginalName).upper()
        return filename.upper()

    def save_xml(self, path):
        """
        Creates and serilizes XML for Orphea
        :return: None
        """

        if not path:
            raise ValueError('path is not set!')

        filename = None

        # if not self.IsReady:
        if not self.is_ready():
            raise ValueError('Data is not ready!')

        root = et.Element("assets")

        if self.FixedIdentifier is not None:
            et.SubElement(root, "fixident").text = self.FixedIdentifier
            filename = os_path.join(path, "{}.xml".format(self.FixedIdentifier))

        if self.Id is not None:
            et.SubElement(root, "id_objet").text = self.Id
            filename = os_path.join(path, "{}.xml".format(self.Id))

        if self.Title:
            et.SubElement(root, "title").text = self.Title

        #if self.Caption:
        new_caption = self.SetNewCaption()
        et.SubElement(root, "captionweb").text = new_caption
        et.SubElement(root, "subtitle").text = new_caption
        et.SubElement(root, "caption").text = new_caption

        if self.CreationDate:
            et.SubElement(root, "creationdate").text = self.CreationDate.strftime("%d.%m.%Y")

        if self.Credit:
            et.SubElement(root, "credit").text = self.Credit

        if self.Byline:
            et.SubElement(root, "byline").text = self.Byline
        else:
            if self.Author:
                et.SubElement(root, "byline").text = self.Author

        et.SubElement(root, "original_filename").text = self.get_filename()

        if filename:
            tree = et.ElementTree(root)
            tree.write(filename, encoding='utf-8', xml_declaration=True)

    def save_xml_2(self, path):
        """
        Creates and serilizes XML for Orphea
        :return: None
        """

        if not path:
            raise ValueError('path is not set!')

        filename = None

        #if not self.IsReady:
        #    raise ValueError('Data is not ready!')

        root = et.Element("assets")

        if self.FixedIdentifier is not None:
            et.SubElement(root, "fixident").text = self.FixedIdentifier
            filename = os_path.join(path, "{}.xml".format(self.FixedIdentifier))

        if self.Id is not None:
            et.SubElement(root, "id_objet").text = self.Id
            filename = os_path.join(path, "{}.xml".format(self.Id))

        if self.Title:
            et.SubElement(root, "title").text = self.Title

        #if self.Caption:
        new_caption = self.SetNewCaption()

        # TODO: если фото в одном из закрытых контрактных библиотеках -
        #et.SubElement(root, "captionweb").text = new_caption
        et.SubElement(root, "subtitle").text = new_caption
        #et.SubElement(root, "caption").text = new_caption

        if self.CreationDate:
            et.SubElement(root, "creationdate").text = self.CreationDate.strftime("%d.%m.%Y")

        if self.Credit:
            et.SubElement(root, "credit").text = self.Credit

        if self.Byline:
            et.SubElement(root, "byline").text = self.Byline
        else:
            if self.Author:
                et.SubElement(root, "byline").text = self.Author

        if self.OriginalName:
            et.SubElement(root, "original_filename").text = self.get_filename()

        if filename:
            tree = et.ElementTree(root)
            tree.write(filename, encoding='utf-8', xml_declaration=True)

    def SetNewCaption(self):
        """Update caption with licence info
        :return: new caption with additions
        """

        if self.Caption is not None:
            caption = self.Caption
        else:
            caption = ""

        if self.Contract is not None:
            caption = u'{}\nДоговор: {}'.format(caption, self.Contract)

        if self.ContractId is not None:
            caption = u'{}\nДоговор ID: {}'.format(caption, self.ContractId)

        if self.Author:
            caption = u'{}\nАвтор: {}'.format(caption, self.Author)

        if self.Byline:
            caption = u'{}\nПсевдоним автора: {}'.format(caption, self.Byline)

        if self.Credit:
            caption = u'{}\nCredit: {}'.format(caption, self.Credit)

        if self.License is not None:
            caption = u'{}\nЛицензия: {}'.format(caption, self.License)

        if self.Sublicense is not None:
            caption = u'{}\nСублицензия: {}'.format(caption, self.Sublicense)

        if self.LicenseStartDate is not None or self.LicenseEndDate is not None:
            caption = u'{}\nСрок лицензии:'.format(caption)
            if self.LicenseStartDate is not None:
                caption = u'{} с {}'.format(caption, self.LicenseStartDate.strftime("%d.%m.%Y"))

            if self.LicenseEndDate is not None:
                caption = u'{} по {}'.format(caption, self.LicenseEndDate.strftime("%d.%m.%Y"))

        if self.Type_of_use is not None:
            caption = u'{}\nРазрешено использование: {}'.format(caption, self.Type_of_use)

        if self.Territory is not None:
            caption = u'{}\nТерритория использования: {}'.format(caption, self.Territory)

        if self.Publishing is not None:
            caption = u'{}\nРедакция: {}'.format(caption, self.Publishing)

        if self.OriginalName is not None:
            caption = u'{}\nИмя файла: {}'.format(caption, self.OriginalName)

        return caption