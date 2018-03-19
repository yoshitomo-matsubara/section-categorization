import matplotlib.pyplot as plt
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
        count = 0
        size = feature_mat.shape[0]
        for section_number, label, features in\
                sorted(zip(label_mat[:, 2].tolist(), label_mat[:, 0].tolist(), feature_mat.tolist())):
            count += 1
            self.labels.append(str(label))
            feature_dict = dict()
            for i in range(len(features)):
                if features[i] != 0.0:
                    feature_dict[str(i)] = features[i]
            feature_dict['FIRST_SECTION'] = 1 if count == 1 else 0
            feature_dict['LAST_SECTION'] = 1 if count == size else 0
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


def plot_error_bar_chart(error_dict, output_file_path, length=0.8,
                         colors=['red', 'green', 'blue', 'orange', 'lime', 'cyan']):
    index = 0
    unit_length = length / len(config.LABELS)
    for true_label in config.LABELS:
        x = index - length / 2
        sub_index = 0
        sub_dict = error_dict[true_label] if true_label in error_dict.keys() else None
        for pred in config.LABELS:
            freq = sub_dict[pred] if sub_dict is not None and pred in sub_dict.keys() else 0
            if index == 0:
                plt.bar(x + unit_length * sub_index, freq, width=0.1, color=colors[sub_index],
                        label='Predicted as ' + pred)
            else:
                plt.bar(x + unit_length * sub_index, freq, width=0.1, color=colors[sub_index])
            sub_index += 1
        index += 1

    plt.xticks(list(range(len(config.LABELS))), config.LABELS, fontsize=12)
    plt.xlabel('True Labels', fontsize=16)
    plt.ylabel('False Negative Frequency', fontsize=16)
    plt.legend(fontsize=12)
    if output_file_path is not None:
        file_util.make_parent_dirs(output_file_path)
        plt.savefig(output_file_path, type='eps', bbox_inches='tight')
    plt.show()


def error_analysis(true_labels, preds, output_file_path):
    error_dict = dict()
    for (true_label, pred) in zip(true_labels, preds):
        if true_label == pred:
            continue

        if true_label not in error_dict.keys():
            error_dict[true_label] = dict()

        if pred not in error_dict[true_label].keys():
            error_dict[true_label][pred] = 0

        error_dict[true_label][pred] += 1
    plot_error_bar_chart(error_dict, output_file_path)


def sequential_error_analysis(list_of_labels, list_of_preds, output_file_path):
    error_dict = dict()
    for (labels, preds) in zip(list_of_labels, list_of_preds):
        for (true_label, pred) in zip(labels, preds):
            if true_label == pred:
                continue

            if true_label not in error_dict.keys():
                error_dict[true_label] = dict()

            if pred not in error_dict[true_label].keys():
                error_dict[true_label][pred] = 0

            error_dict[true_label][pred] += 1
    plot_error_bar_chart(error_dict, output_file_path)
