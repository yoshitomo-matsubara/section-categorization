import argparse
import numpy as np
import os
from util import file_util, config


DELIMITER = '_'
TRAINING = 'training'
VALIDATION = 'validation'
TEST = 'test'


def split(paper_dir_list, ratios, rand):
    np.random.seed(0)
    ratios = list(map(float, ratios))
    index = 1 if len(os.path.basename(paper_dir_list[0]).split(DELIMITER)) == 1 else 3
    paper_dir_list = sorted(paper_dir_list, key=lambda path: DELIMITER.join(os.path.basename(path).split('_')[index:]))\
        if not rand else np.random.shuffle(paper_dir_list)
    paper_dir_size = len(paper_dir_list)
    total_size = sum(ratios)
    training_size = int(ratios[0] / total_size * paper_dir_size)
    validation_size = int(ratios[1] / total_size * paper_dir_size)
    validation_index = training_size
    test_index = validation_index + validation_size
    return paper_dir_list[: validation_index], paper_dir_list[validation_index:test_index], paper_dir_list[test_index:]


def output_dirs(path_list, type, base_output_dir_path):
    output_dir_path = os.path.join(base_output_dir_path, type)
    for path in path_list:
        base_name = os.path.basename(path)
        # print(os.path.join(output_dir_path, base_name))
        file_util.copy_dir(path, os.path.join(output_dir_path, base_name))


def main(args):
    paper_dir_list = file_util.get_dir_list(args.input)
    training_path_list, validation_path_list, test_path_list = split(paper_dir_list, args.ratio.split(':'), args.rand)
    output_dirs(training_path_list, TRAINING, args.output)
    output_dirs(validation_path_list, VALIDATION, args.output)
    output_dirs(test_path_list, TEST, args.output)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description=os.path.basename(__file__))
    arg_parser.add_argument('-input', required=True, help='[input] labeled text dir path')
    arg_parser.add_argument('-ratio', required=False, default='7:1:2', help='[optional] ratios of training, validation'
                                                                            'and test datasets separated by a colon')
    arg_parser.add_argument('-rand', action='store_true', help='[optional] randomly sample')
    arg_parser.add_argument('-output', required=True, help='[output] output dir path')
    main(arg_parser.parse_args())
