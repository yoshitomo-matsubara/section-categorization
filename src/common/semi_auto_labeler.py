import argparse
import os
from util import file_util, config


CONCLUSION_WORDS = ['conclusion', 'conclud', 'summary']
RELATED_WORDS = ['related', 'previous']
INTRO_WORDS = ['introduction', 'intro', 'motivation', 'background']
EXPERIMENT_WORDS = ['experiment', 'discussion', 'evaluation', 'result']
APPROACH_WORDS = ['approach', 'proposed', 'method']


def substring_match(section_title, words):
    for word in words:
        if section_title.find(word) >= 0:
            return True
    return False


def try_labelling(input_file_path):
    if os.path.basename(input_file_path).startswith(config.ABSTRACT_LABEL):
        return None

    header = file_util.read_header(input_file_path)
    section_title = header.split(config.BASE_DELIMITER)[1].lower()
    if substring_match(section_title, CONCLUSION_WORDS):
        return config.CONCLUSION_LABEL
    if substring_match(section_title, RELATED_WORDS):
        return config.RELATED_LABEL
    if substring_match(section_title, INTRO_WORDS):
        return config.INTRO_LABEL
    if substring_match(section_title, EXPERIMENT_WORDS):
        return config.EXPERIMENT_LABEL
    if substring_match(section_title, APPROACH_WORDS):
        return config.APPROACH_LABEL
    return None


def main(args):
    input_dir_path_list = file_util.get_dir_list(args.input)
    for input_dir_path in input_dir_path_list:
        input_file_path_list = file_util.get_file_list(input_dir_path)
        dir_name = os.path.basename(input_dir_path)
        output_dir_path = os.path.join(args.output, dir_name)
        for input_file_path in input_file_path_list:
            label = try_labelling(input_file_path)
            file_name = label + os.path.basename(input_file_path) if label is not None\
                else os.path.basename(input_file_path)
            file_util.copy_file(input_file_path, os.path.join(output_dir_path, file_name))


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description=os.path.basename(__file__))
    arg_parser.add_argument('-input', required=True, help='[input] cleaned text dir path')
    arg_parser.add_argument('-output', required=True, help='[output] output dir path')
    main(arg_parser.parse_args())
