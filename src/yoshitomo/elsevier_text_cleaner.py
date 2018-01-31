import argparse
import os
import xml.etree.ElementTree as ET


ROOT_NS = '{http://www.elsevier.com/xml/svapi/article/dtd}'
DOC_NS = '{http://www.elsevier.com/xml/xocs/dtd}'
ARTICLE_NS = '{http://www.elsevier.com/xml/ja/dtd}'
CE_NS = '{http://www.elsevier.com/xml/common/dtd}'


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
        print(self.xml_file_path)
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


def get_file_path_list_and_name_set(input_dir_path):
    file_path_dict = dict()
    for dir_name in os.listdir(input_dir_path):
        dir_path = os.path.join(input_dir_path, dir_name)
        if os.path.isdir(dir_path):
            for file_name in os.listdir(dir_path):
                file_path = os.path.join(dir_path, file_name)
                if os.path.isfile(file_path):
                    file_name_wo_ext = os.path.basename(os.path.splitext(file_path)[0])
                    file_path_dict[file_name_wo_ext] = file_path
    return file_path_dict


def get_paper_list(xml_dir_path, raw_dir_path):
    xml_file_path_dict = get_file_path_list_and_name_set(xml_dir_path)
    raw_file_path_dict = get_file_path_list_and_name_set(raw_dir_path)
    paper_list = list()
    for xml_file_name in xml_file_path_dict.keys():
        if xml_file_name in raw_file_path_dict:
            paper_list.append(Paper(xml_file_path_dict[xml_file_name], raw_file_path_dict[xml_file_name]))
        else:
            print('Could not find a pair of', xml_file_name, ' xml and txt files')
    return paper_list


def clean(paper, base_output_dir_path):
    paper.read_files()
    complete = paper.extract_structure()
    if not complete:
        return False
    paper.extract_first_and_last_blocks()
    return True

    # output_dir_path = os.path.join(base_output_dir_path, dir_name)
    # if not os.path.exists(output_dir_path):
    #     os.makedirs(output_dir_path)


def main(args):
    paper_list = get_paper_list(args.xml, args.raw)
    count = 0
    for paper in paper_list:
        complete = clean(paper, args.output)
        if complete:
            count += 1


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description=os.path.basename(__file__))
    arg_parser.add_argument('-xml', required=True, help='[input] xml text dir path')
    arg_parser.add_argument('-raw', required=True, help='[input] raw text dir path')
    arg_parser.add_argument('-output', required=True, help='[output] output dir path')
    main(arg_parser.parse_args())
