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
        self.title = title.strip() if title is not None else ''
        self.index = index
        self.prefix = str(self.index) + ' ' + self.title
        self.text = None
        self.ref_id_list = list()
        self.ref_id_set = list()

    def add_child(self, title):
        idx = len(self.child_list) + 1
        self.child_list.append(Section(title, idx))

    def header(self):
        ref_id_list_str = ','.join(self.ref_id_list)
        return '\t'.join([str(self.index), self.title, str(len(self.child_list)),
                          str(len(self.ref_id_set)), ref_id_list_str])


class Paper:
    CONCLUSION_SUFFIXES = [' Acknowledgement', ' Acknowledgment', ' Reference', '   ', ' Appendix']

    def __init__(self, modified_doi, xml_file_path, raw_file_path):
        self.modified_doi = modified_doi
        self.xml_file_path = xml_file_path
        self.raw_file_path = raw_file_path
        self.xml_tree = None
        self.raw_lines = None
        self.abstract = None
        self.toc_list = list()
        self.section_list = list()
        self.body_lines = list()

    def read_files(self):
        self.xml_tree = ET.parse(self.xml_file_path)
        with open(self.raw_file_path, 'r') as fp:
            self.raw_lines = fp.readlines()

    def add_section(self, child):
        section_element = child.find(DOC_NS + 'item-toc-section-title')
        section = Section(section_element.text, len(self.toc_list) + 1)
        if child.find(DOC_NS + 'item-toc-entry') is not None:
            for sub_child in child.findall(DOC_NS + 'item-toc-entry'):
                subsection_element = sub_child.find(DOC_NS + 'item-toc-section-title')
                section.add_child(subsection_element.text)
        self.toc_list.append(section)

    def extract_structure(self):
        root = self.xml_tree.getroot()
        doc = root.find(ROOT_NS + 'originalText').find(DOC_NS + 'doc')
        meta = doc.find(DOC_NS + 'meta')
        item_toc = meta.find(DOC_NS + 'item-toc')
        if item_toc is None:
            return False
        for child in item_toc.getchildren():
            self.add_section(child)

        serial_item = doc.find(DOC_NS + 'serial-item')
        if serial_item is None:
            return False

        article = serial_item.find(ARTICLE_NS + 'article')
        if article is None:
            return False

        body = article.find(ARTICLE_NS + 'body')
        if body is None:
            return False

        sections = body.find(CE_NS + 'sections')
        if sections is None:
            return False

        toc_index = 0
        for child in sections.getchildren():
            toc_index += 1
            if child is None:
                continue

            section_title = child.find(CE_NS + 'section-title')
            if section_title is None:
                return False

            title = section_title.text
            if title != self.toc_list[toc_index - 1].title:
                return False

            raw_xml_text = str(ET.tostring(child))
            index = raw_xml_text.find('refid')
            ref_id_list = list()
            while index >= 0:
                raw_xml_text = raw_xml_text[index:]
                start_idx = raw_xml_text.find('\"')
                raw_xml_text = raw_xml_text[start_idx + 1:]
                end_idx = raw_xml_text.find('\"')
                ref_id_str = raw_xml_text[:end_idx]
                index = raw_xml_text.find('refid')
                ref_ids = ref_id_str.split(' ')
                for ref_id in ref_ids:
                    if ref_id.lower().startswith('b'):
                        ref_id_list.append(ref_id)
            self.toc_list[toc_index - 1].ref_id_list.extend(ref_id_list)
            self.toc_list[toc_index - 1].ref_id_set = set(self.toc_list[toc_index - 1].ref_id_list)
        return True

    def extract_abstract(self, abstract_prefix='Abstract', abstract_suffix='0 false'):
        index = 0
        abstract_str = None
        for line in self.raw_lines:
            if abstract_str is None and line.find(abstract_prefix) >= 0:
                abstract_str = line[line.find(abstract_prefix):]
            elif line.find(abstract_suffix) >= 0:
                if abstract_str is None:
                    return False
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
                section_prefix = self.toc_list[0].prefix
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
        return len(self.body_lines) > 0

    def extract_sections(self):
        body_line = '\n'.join(self.body_lines)
        for section in self.toc_list:
            if section.prefix is not None and body_line.find(section.prefix) >= 0:
                self.section_list.append(section)

        last_index = len(self.section_list) - 1
        complete = False
        for index in range(len(self.section_list)):
            section = self.section_list[index]
            section_prefix = section.prefix
            if body_line.find(section_prefix) < 0:
                continue

            if index < last_index:
                next_section = self.toc_list[index + 1]
                section_suffix = str(next_section.index) + ' ' + next_section.title
                section.text =\
                    body_line[body_line.find(section_prefix) + len(section_prefix) + 1:body_line.find(section_suffix)]
                body_line = body_line[body_line.find(section_suffix):]
            else:
                valid_index_list = list()
                for conclusion_suffix in self.CONCLUSION_SUFFIXES:
                    index = body_line.find(conclusion_suffix)
                    if index >= 0:
                        valid_index_list.append(index)

                if len(valid_index_list) == 0:
                    return False
                section.text = body_line[body_line.find(section_prefix) + len(section_prefix) + 1:min(valid_index_list)]
                complete = True
        return complete
