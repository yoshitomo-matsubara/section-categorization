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


def make_parent_dirs(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def read_header(file_path):
    with open(file_path, 'r') as fp:
        header = fp.readline()
    return header


def copy_file(src_file_path, dst_file_path):
    parent_dir_path = os.path.abspath(os.path.dirname(dst_file_path))
    make_parent_dirs(parent_dir_path)
    shutil.copy(src_file_path, dst_file_path)
