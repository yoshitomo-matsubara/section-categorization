import argparse
import numpy as np
import os
from sklearn.feature_extraction.text import CountVectorizer
from util import file_util, config


def extract_header_features(file_line_matrix):
    file_header_list = list()
    for file_line_list in file_line_matrix:
        file_header_list.append(file_line_list[0])

    file_size = len(file_header_list)
    header_feature_mat = np.zeros((file_size, 5))
    for i in range(file_size):
        elements = file_header_list[i].split(config.BASE_DELIMITER)
        header_feature_mat[i][0] = int(elements[2])
        header_feature_mat[i][1] = int(elements[3])
        header_feature_mat[i][2] = int(elements[5])
        header_feature_mat[i][3] = int(elements[7])
        header_feature_mat[i][4] = int(elements[9])
    return header_feature_mat


def extract_features(input_file_path_list, min_df, transformed_vectorizer):
    file_line_list = file_util.read_files_as_line_list(input_file_path_list, start_idx=1)
    file_line_matrix = file_util.read_files(input_file_path_list)
    header_feature_mat = extract_header_features(file_line_matrix)
    min_df = 1 if min_df < 0 else min_df
    if transformed_vectorizer is None:
        vectorizer = CountVectorizer(min_df=min_df, stop_words='english', binary=True)
        vectorizer.fit(file_line_list)
        return vectorizer, vectorizer.fit_transform(file_line_list), header_feature_mat
    return transformed_vectorizer, transformed_vectorizer.transform(file_line_list), header_feature_mat


def detect_abstract_file(input_file_path_list):
    file_size = len(input_file_path_list)
    file_label_path_mat = list()
    non_abstract_flags = list()
    for i in range(file_size):
        file_path = input_file_path_list[i]
        file_name = os.path.basename(file_path)
        file_label_path_list = list()
        file_label_path_list.append(file_name.split(config.FILE_DELIMITER)[0])
        file_label_path_list.append(file_path)
        file_label_path_list.append(file_util.read_header(file_path).split(config.BASE_DELIMITER)[0])
        file_label_path_mat.append(file_label_path_list)
        non_abstract_flags.append(not file_name.startswith(config.ABSTRACT_LABEL))
    return np.array(file_label_path_mat), non_abstract_flags


def extract(base_input_dir_path, data_type, min_df, vectorizer, base_output_dir_path):
    input_dir_path = os.path.join(base_input_dir_path, data_type, config.RAW)
    input_file_path_list = file_util.get_file_list(input_dir_path, is_recursive=True)
    transformed_vectorizer, feature_mat, header_feature_mat = extract_features(input_file_path_list, min_df, vectorizer)
    file_label_path_mat, non_abstract_flags = detect_abstract_file(input_file_path_list)
    output_dir_path = os.path.join(base_output_dir_path, data_type, config.EXTRACTED)
    output_file_path = os.path.join(output_dir_path, config.FEATURE_FILE_NAME)
    file_util.make_parent_dirs(output_file_path)
    with open(output_file_path, 'w') as fp:
        for i in range(len(non_abstract_flags)):
            if not non_abstract_flags[i]:
                continue
            output_mat = np.concatenate([np.atleast_2d(header_feature_mat[i]),
                                         np.atleast_2d(feature_mat[i].todense())], axis=1)
            output_mat = output_mat.astype(np.str)
            fp.write(config.BASE_DELIMITER.join(output_mat.tolist()[0]) + '\n')
    output_label_file_path = os.path.join(output_dir_path, config.LABEL_FILE_NAME)
    np.savetxt(output_label_file_path, file_label_path_mat[non_abstract_flags, :],
               delimiter=config.BASE_DELIMITER, fmt='%s')
    return transformed_vectorizer


def main(args):
    transformed_vectorizer = extract(args.input, config.TRAINING, args.mindf, None, args.output)
    extract(args.input, config.VALIDATION, args.mindf, transformed_vectorizer, args.output)
    extract(args.input, config.TEST, args.mindf, transformed_vectorizer, args.output)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description=os.path.basename(__file__))
    arg_parser.add_argument('-input', required=True, help='[input] dataset dir path')
    arg_parser.add_argument('-mindf', required=False, type=int, default=200, help='[param] min document frequency')
    arg_parser.add_argument('-output', required=True, help='[output] output dir path')
    main(arg_parser.parse_args())
