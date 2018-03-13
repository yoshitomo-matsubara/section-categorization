import os
import shutil


def get_file_list(dir_path, is_recursive=False):
    file_list = list()
    for file in os.listdir(dir_path):
        path = os.path.join(dir_path, file)
        if os.path.isfile(path):
            file_list.append(path)
        elif is_recursive:
            file_list.extend(get_file_list(path, is_recursive))
    return file_list


def get_dir_list(dir_path, is_recursive=False):
    dir_list = list()
    for file in os.listdir(dir_path):
        path = os.path.join(dir_path, file)
        if os.path.isdir(path):
            dir_list.append(path)
        elif is_recursive:
            dir_list.extend(get_dir_list(path, is_recursive))
    return dir_list


def make_dirs(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def make_parent_dirs(file_path):
    dir_path = os.path.dirname(file_path)
    make_dirs(dir_path)


def read_header(file_path):
    with open(file_path, 'r') as fp:
        header = fp.readline().strip()
    return header


def read_file(file_path):
    line_list = list()
    with open(file_path, 'r') as fp:
        for line in fp.readlines():
            line_list.append(line.strip())
    return line_list


def read_files(file_path_list):
    file_line_matrix = list()
    for file_path in file_path_list:
        file_line_matrix.append(read_file(file_path))
    return file_line_matrix


def read_file_as_line(file_path, start_idx=0):
    line_list = read_file(file_path)
    return ' '.join(line_list[start_idx:])


def read_files_as_line_list(file_path_list, start_idx=0):
    file_line_list = list()
    for file_path in file_path_list:
        file_line_list.append(read_file_as_line(file_path, start_idx))
    return file_line_list


def copy_file(src_file_path, dst_file_path):
    make_parent_dirs(dst_file_path)
    shutil.copy(src_file_path, dst_file_path)


def copy_dir(src_dir_path, dst_dir_path):
    make_parent_dirs(dst_dir_path)
    shutil.copytree(src_dir_path, dst_dir_path)
