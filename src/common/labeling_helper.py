import argparse
import os
from util import file_util, config


DELIMITER = ','
ASSIGNED_LABEL = '#######'


def output_template_list(input_dir_path, output_file_path):
    input_dir_path_list = file_util.get_dir_list(input_dir_path)
    input_file_path_list = list()
    for input_dir_path in input_dir_path_list:
        input_file_path_list.extend(file_util.get_file_list(input_dir_path))

    input_file_path_list.sort()
    file_util.make_parent_dirs(output_file_path)
    with open(output_file_path, 'w') as fp:
        fp.write('File path,Label\n')
        for input_file_path in input_file_path_list:
            input_file_name = os.path.basename(input_file_path)
            if input_file_name.find(config.FILE_DELIMITER) < 0:
                fp.write(input_file_path + DELIMITER + '\n')
            else:
                fp.write(input_file_path + DELIMITER + ASSIGNED_LABEL + '\n')


def check_if_exist(input_file_path):
    if os.path.exists(input_file_path):
        return True
    print('Could not find ', input_file_path)
    return False


def assign_labels(list_file_path, output_dir_path):
    count = -1
    with open(list_file_path, 'r') as fp:
        for line in fp.readlines():
            line = line.strip()
            count += 1
            if count == 0 or len(line) == 0:
                continue

            elements = line.split(DELIMITER)
            input_file_path = elements[0]
            if not os.path.exists(input_file_path):
                print('Could not find ', input_file_path, 'Label:', elements[1])
                continue

            output_parent_dir_path = os.path.basename((os.path.dirname(input_file_path)))
            output_file_name = os.path.basename(input_file_path)
            if len(elements[1]) == 1:
                output_file_name = elements[1] + config.FILE_DELIMITER + output_file_name

            output_file_path = os.path.join(output_dir_path, output_parent_dir_path, output_file_name)
            file_util.copy_file(input_file_path, output_file_path)


def main(args):
    if args.input is not None:
        output_template_list(args.input, args.list)
    elif os.path.exists(args.list) and args.output is not None:
        assign_labels(args.list, args.output)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description=os.path.basename(__file__))
    arg_parser.add_argument('-input', required=False, help='[input] cleaned text dir path')
    arg_parser.add_argument('-list', required=True, help='[optional, input or output] labeled list file path')
    arg_parser.add_argument('-output', required=False, help='[output] output dir path')
    main(arg_parser.parse_args())
