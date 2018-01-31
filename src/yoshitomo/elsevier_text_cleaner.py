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
    complete = paper.extract_abstract()
    if not complete:
        return False

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
    print(count)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description=os.path.basename(__file__))
    arg_parser.add_argument('-xml', required=True, help='[input] xml text dir path')
    arg_parser.add_argument('-raw', required=True, help='[input] raw text dir path')
    arg_parser.add_argument('-output', required=True, help='[output] output dir path')
    main(arg_parser.parse_args())
