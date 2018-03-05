import numpy as np
import os
import pickle
from . import config, file_util


class Data:
    def __init__(self, dir_path):
        self.dir_path = dir_path
        feature_mat_file_path = os.path.join(dir_path, config.EXTRACTED, config.FEATURE_FILE_NAME)
        label_file_path = os.path.join(dir_path, config.EXTRACTED, config.LABEL_FILE_NAME)
        self.feature_mat = np.loadtxt(feature_mat_file_path, delimiter=config.BASE_DELIMITER)
        self.labels = np.loadtxt(label_file_path, delimiter=config.BASE_DELIMITER, usecols=0, dtype=str)


class Dataset:
    def __init__(self, dataset_dir_path):
        self.dataset_dir_path = dataset_dir_path
        self.training = Data(os.path.join(self.dataset_dir_path, config.TRAINING))
        self.validation = Data(os.path.join(self.dataset_dir_path, config.VALIDATION))
        self.test = Data(os.path.join(self.dataset_dir_path, config.TEST))


def get_param_list(param_str):
    param_strs = param_str.split(config.PARAM_RANGE_DELIMITER)
    if len(param_strs) == 4:
        return np.logspace(float(param_strs[0]), float(param_strs[1]), num=int(param_strs[2]), base=float(param_strs[3]))
    return np.linspace(float(param_strs[0]), float(param_strs[1]), num=int(param_strs[2]))


def load_model(model_file_path):
    if model_file_path is None or not os.path.exists(model_file_path):
        return None

    with open(model_file_path, 'rb') as fp:
        return pickle.load(fp)


def save_model(model, model_file_path):
    file_util.make_parent_dirs(model_file_path)
    with open(model_file_path, 'wb') as fp:
        pickle.dump(model, fp)
