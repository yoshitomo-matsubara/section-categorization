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


class Paper:
    def __init__(self, paper_id, feature_mat, label_mat):
        self.paper_id = paper_id
        self.feature_dicts = list()
        self.labels = list()
        for section_number, label, features in sorted(zip(label_mat[:, 2].tolist(), label_mat[:, 0].tolist(), feature_mat.tolist())):
            self.labels.append(str(label))
            feature_dict = dict()
            for i in range(len(features)):
                if features[i] != 0.0:
                    feature_dict[str(i)] = features[i]
            self.feature_dicts.append(feature_dict)


class PaperData:
    def __init__(self, dir_path):
        self.dir_path = dir_path
        self.list_of_feature_dicts = list()
        self.list_of_labels = list()

    @staticmethod
    def extract_idx_list_dict(file_paths):
        idx_list_dict = dict()
        for i in range(len(file_paths)):
            paper_id = os.path.basename(os.path.dirname(file_paths[i]))
            if paper_id not in idx_list_dict.keys():
                idx_list_dict[paper_id] = list()
            idx_list_dict[paper_id].append(i)
        return idx_list_dict

    def process(self):
        feature_mat_file_path = os.path.join(self.dir_path, config.EXTRACTED, config.FEATURE_FILE_NAME)
        label_file_path = os.path.join(self.dir_path, config.EXTRACTED, config.LABEL_FILE_NAME)
        feature_mat = np.loadtxt(feature_mat_file_path, delimiter=config.BASE_DELIMITER)
        label_mat = np.loadtxt(label_file_path, delimiter=config.BASE_DELIMITER, dtype=str)
        idx_list_dict = self.extract_idx_list_dict(label_mat[:, 1])
        for paper_id in idx_list_dict.keys():
            idx_list = idx_list_dict[paper_id]
            paper = Paper(paper_id, feature_mat[idx_list, :], label_mat[idx_list, :])
            self.list_of_feature_dicts.append(paper.feature_dicts)
            self.list_of_labels.append(paper.labels)


class PaperDataset:
    def __init__(self, dataset_dir_path):
        self.dataset_dir_path = dataset_dir_path
        self.training = PaperData(os.path.join(self.dataset_dir_path, config.TRAINING))
        self.validation = PaperData(os.path.join(self.dataset_dir_path, config.VALIDATION))
        self.test = PaperData(os.path.join(self.dataset_dir_path, config.TEST))
        self.training.process()
        self.validation.process()
        self.test.process()


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
