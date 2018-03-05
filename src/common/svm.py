import argparse
import numpy as np
import os
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report
from util import experiment_util


def parameter_tuning(args, dataset):
    c_params = experiment_util.get_param_list(args.c)
    best_valid_acc = -np.inf
    best_c_param = -np.inf
    best_model = None
    for c_param in c_params:
        svm = SVC(C=c_param)
        svm.fit(dataset.training.feature_mat, dataset.training.labels)
        preds = svm.predict(dataset.validation.feature_mat)
        valid_acc = accuracy_score(dataset.validation.labels, preds)
        if valid_acc > best_valid_acc:
            best_valid_acc = valid_acc
            best_c_param = c_param
            best_model = svm
    print('Best validation accuracy:', best_valid_acc, 'Best C:', best_c_param)
    return best_model


def main(args):
    dataset = experiment_util.Dataset(args.input)
    model = experiment_util.load_model(args.model)
    if model is None:
        model = parameter_tuning(args, dataset)
        if args.model is not None:
            experiment_util.save_model(model, args.model)
    preds = model.predict(dataset.test.feature_mat)
    print(classification_report(dataset.test.labels, preds))


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description=os.path.basename(__file__))
    arg_parser.add_argument('-input', required=True, help='[input] dataset dir path')
    arg_parser.add_argument('-model', required=False, help='[optional, input, output]'
                                                                                ' model file path')
    arg_parser.add_argument('-c', required=False, default='-2:2:5:10', help='[optional, param] C parameter')
    arg_parser.add_argument('-output', required=True, help='[output] output dir path')
    main(arg_parser.parse_args())