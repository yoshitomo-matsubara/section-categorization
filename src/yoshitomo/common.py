import requests
import xml.etree.ElementTree as ET


ELSEVIER_API_KEY_FILE_PATH = './resource/elsevier_api_key.txt'
ROOT_NS = '{http://www.elsevier.com/xml/svapi/article/dtd}'
DOC_NS = '{http://www.elsevier.com/xml/xocs/dtd}'
ARTICLE_NS = '{http://www.elsevier.com/xml/ja/dtd}'
CE_NS = '{http://www.elsevier.com/xml/common/dtd}'


class Elsevier:
    SEARCH_BASE_URL = 'https://api.elsevier.com/content/search/scidir'
    ARTICLE_BASE_URL = 'https://api.elsevier.com/content/article/doi/'

    def __init__(self):
        with open(ELSEVIER_API_KEY_FILE_PATH) as fp:
            self.api_key = fp.readline().strip()

    def send_request(self, base_url, options):
        option_str = '&'.join(options)
        response = requests.get(base_url + '?APIKey=' + self.api_key + '&' + option_str)
        return response

    def search_request(self, options):
        response = self.send_request(self.SEARCH_BASE_URL, options)
        return response.content

    def text_request(self, doi, options=[]):
        response = self.send_request(self.ARTICLE_BASE_URL + doi, options)
        return response.content


class Section:
    def __init__(self, title, index):
        self.child_list = list()
        self.title = title
        self.index = index
        self.first_block = None
        self.last_block = None

    def add_child(self, title):
        idx = len(self.child_list) + 1
        self.child_list.append(Section(title, idx))

    def add_block(self, block):
        if self.first_block is None:
            self.first_block = block
        else:
            self.last_block = block


class Paper:
    def __init__(self, xml_file_path, raw_file_path):
        self.xml_file_path = xml_file_path
        self.raw_file_path = raw_file_path
        self.xml_tree = None
        self.raw_lines = None
        self.section_list = list()
        self.abstract = None
        self.body_lines = list()

    def read_files(self):
        self.xml_tree = ET.parse(self.xml_file_path)
        with open(self.raw_file_path, 'r') as fp:
            self.raw_lines = fp.readlines()

    def add_section(self, child):
        section_element = child.find(DOC_NS + 'item-toc-section-title')
        section = Section(section_element.text, len(self.section_list) + 1)
        if child.find(DOC_NS + 'item-toc-entry') is not None:
            for sub_child in child.findall(DOC_NS + 'item-toc-entry'):
                subsection_element = sub_child.find(DOC_NS + 'item-toc-section-title')
                section.add_child(subsection_element.text)
        self.section_list.append(section)

    def extract_structure(self):
        root = self.xml_tree.getroot()
        meta = root.find(ROOT_NS + 'originalText').find(DOC_NS + 'doc').find(DOC_NS + 'meta')
        item_toc = meta.find(DOC_NS + 'item-toc')
        if item_toc is None:
            return False
        for child in item_toc.getchildren():
            self.add_section(child)
        return True

    def extract_first_and_last_blocks(self):
        root = self.xml_tree.getroot()
        serial_item = root.find(ROOT_NS + 'originalText').find(DOC_NS + 'doc').find(DOC_NS + 'serial-item')
        article = serial_item.find(ARTICLE_NS + 'article')
        if article is None:
            article = serial_item.find(ARTICLE_NS + 'converted-article')
        sections = article.find(ARTICLE_NS + 'body').find(CE_NS + 'sections')
        valid_section_list = list()
        for section in sections:
            if section.find(CE_NS + 'label') is not None:
                valid_section_list.append(section)

        index = 0
        last_index = len(valid_section_list) - 1
        for section in valid_section_list:
            label = section.find(CE_NS + 'label').text
            title = section.find(CE_NS + 'section-title').text
            block = label + ' ' + title
            if index < last_index and section.find(CE_NS + 'para') is not None:
                para = section.find(CE_NS + 'para').text
                block += ' ' + para
            self.section_list[index].add_block(block)
            if index > 0:
                self.section_list[index - 1].add_block(block)
            if index == last_index:
                paras = section.findall(CE_NS + 'para')
                if len(paras) == 0:
                    sub_sections = section.findall(CE_NS + 'section')
                    paras = sub_sections[-1].findall(CE_NS + 'para')

                para = paras[len(paras) - 1].text
                self.section_list[index].add_block(para)
            index += 1

    def extract_abstract(self, abstract_prefix='Abstract', abstract_suffix='0 false'):
        index = 0
        abstract_str = None
        for line in self.raw_lines:
            if abstract_str is None and line.find(abstract_prefix) >= 0:
                abstract_str = line[line.find(abstract_prefix):]
            elif line.find(abstract_suffix) >= 0:
                abstract_str += line[:line.find(abstract_suffix)]
                break
            elif abstract_str is not None:
                abstract_str += line
            index += 1
        self.abstract = abstract_str
        cut_lines = self.raw_lines[index:]
        is_abs_first_sect_in_line = True
        for line in cut_lines:
            if line.find(abstract_prefix) >= 0 and is_abs_first_sect_in_line:
                section_prefix = str(self.section_list[0].index) + ' ' + self.section_list[0].title
                if line.find(section_prefix, line.find(abstract_prefix)) >= 0:
                    extracted_line = line[line.find(section_prefix, line.find(abstract_prefix)):]
                    self.body_lines.append(extracted_line)
                else:
                    is_abs_first_sect_in_line = False
            elif not is_abs_first_sect_in_line and line.find(section_prefix) >= 0:
                    extracted_line = line[line.find(section_prefix):]
                    self.body_lines.append(extracted_line)
            elif len(self.body_lines) > 0:
                self.body_lines.append(line)
        # print(self.body_lines)
        print(self.xml_file_path)
        return len(self.body_lines) > 0
