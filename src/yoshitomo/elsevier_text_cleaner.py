import argparse
import os
from common import Paper


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
    for modified_doi in xml_file_path_dict.keys():
        if modified_doi in raw_file_path_dict:
            paper_list.append(Paper(modified_doi, xml_file_path_dict[modified_doi], raw_file_path_dict[modified_doi]))
        else:
            print('Could not find a pair of', modified_doi, ' xml and txt files')
    return paper_list


def clean(paper, base_output_dir_path):
    paper.read_files()
    complete = paper.extract_structure()
    if not complete:
        return False
    complete = paper.extract_abstract()
    if not complete:
        return False
    complete = paper.extract_sections()
    if not complete:
        return False

    if not os.path.exists(base_output_dir_path):
        os.makedirs(base_output_dir_path)
    output_file_path = os.path.join(base_output_dir_path, paper.modified_doi + '.txt')
    for section in paper.section_list:
        if section.prefix is None or section.text is None:
            return False
    with open(output_file_path, 'w') as fp:
        for section in paper.section_list:
            fp.write(section.prefix + '\n')
            fp.write(section.text + '\n\n')
    return True


def main(args):
    paper_list = get_paper_list(args.xml, args.raw)
    count = 0
    for paper in paper_list:
        complete = clean(paper, args.output)
        if complete:
            count += 1
    print('Cleaned', count, '/', len(paper_list))


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description=os.path.basename(__file__))
    arg_parser.add_argument('-xml', required=True, help='[input] xml text dir path')
    arg_parser.add_argument('-raw', required=True, help='[input] raw text dir path')
    arg_parser.add_argument('-output', required=True, help='[output] output dir path')
    main(arg_parser.parse_args())
