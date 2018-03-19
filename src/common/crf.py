import argparse
import numpy as np
import os
from sklearn_crfsuite import CRF
from sklearn_crfsuite import metrics
from util import experiment_util


def parameter_tuning(args, dataset):
    c1s = experiment_util.get_param_list(args.c1)
    c2s = experiment_util.get_param_list(args.c2)
    best_valid_f1_score = -np.inf
    best_c1 = -np.inf
    best_c2 = -np.inf
    best_model = None
    for c1 in c1s:
        for c2 in c2s:
            crf = CRF(algorithm='lbfgs', c1=c1, c2=c2, max_iterations=1000,
                      all_possible_transitions=True, verbose=args.debug)
            crf.fit(dataset.training.list_of_feature_dicts, dataset.training.list_of_labels)
            preds = crf.predict(dataset.validation.list_of_feature_dicts)
            valid_f1_score = metrics.flat_f1_score(dataset.validation.list_of_labels, preds, average='micro')
            if valid_f1_score > best_valid_f1_score:
                best_valid_f1_score = valid_f1_score
                best_c1 = c1
                best_c2 = c2
                best_model = crf
    print('Best validation F1 score:', best_valid_f1_score, 'Best c1:', best_c1, 'Best c2:', best_c2)
    return best_model


def main(args):
    dataset = experiment_util.PaperDataset(args.input)
    model = experiment_util.load_model(args.model)
    if model is None:
        model = parameter_tuning(args, dataset)
        if args.model is not None:
            experiment_util.save_model(model, args.model)
    list_of_preds = model.predict(dataset.test.list_of_feature_dicts)
    print(metrics.flat_classification_report(dataset.test.list_of_labels, list_of_preds))
    print('Micro-averaged F1 score:',
          metrics.flat_f1_score(dataset.test.list_of_labels, list_of_preds, average='micro'))
    experiment_util.sequential_error_analysis(dataset.test.list_of_labels, list_of_preds, args.output)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description=os.path.basename(__file__))
    arg_parser.add_argument('-input', required=True, help='[input] dataset dir path')
    arg_parser.add_argument('-model', required=False, help='[optional, input, output] model file path')
    arg_parser.add_argument('-c1', required=False, default='0:1:10', help='[optional, param] L1 coefficient')
    arg_parser.add_argument('-c2', required=False, default='0:1:10', help='[optional, param] L2 coefficient')
    arg_parser.add_argument('-debug', action='store_true', help='[flag] debug option in training')
    arg_parser.add_argument('-output', required=False, help='[output] output graph file path')
    main(arg_parser.parse_args())
