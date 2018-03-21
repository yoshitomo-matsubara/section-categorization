import argparse
import numpy as np
import os
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from util import experiment_util
import tflearn
import tensorflow as tf
from sklearn.neural_network import MLPClassifier, BernoulliRBM



def MLP(args, dataset):
    # c_params = experiment_util.get_param_list(args.c)
    layes_params = [(50,),(100,),(200,)]
    activation_params = ['identity', 'logistic', 'relu']
    alpha_params = [0.01,0.2,1]
    best_valid_acc = -np.inf
    best_activation_param = ''
    best_model = None
    best_layer_param = 0
    for activation_param in activation_params:
        for alpha_param in alpha_params:
            for layer_param in layes_params:
                classifier = MLPClassifier(hidden_layer_sizes=layer_param, activation=activation_param,alpha=alpha_param, solver='adam')
                classifier.fit(dataset.training.feature_mat, dataset.training.labels)
                preds = classifier.predict(dataset.validation.feature_mat)
                valid_acc = accuracy_score(dataset.validation.labels, preds)
                print(activation_param, alpha_param, layer_param, valid_acc)
                if valid_acc > best_valid_acc:
                    best_valid_acc = valid_acc
                    best_activation_param = activation_param
                    best_layer_param = layer_param
                    best_model = classifier
    print('Best validation accuracy:', best_valid_acc, 'Best activation_param:', best_activation_param,\
    'best alpha: ', alpha_param, 'best layer: ',best_layer_param)
    return best_model



def main(args):
    dataset = experiment_util.Dataset(args.input)
    model = experiment_util.load_model(args.model)
    if model is None:    
        model = MLP(args, dataset)
        if args.model is not None:
            experiment_util.save_model(model, args.model)
    preds = model.predict(dataset.test.feature_mat)
    test_labels = dataset.test.labels
    predicted = preds
    print(classification_report(test_labels, predicted))
    print("F1_micor score on test =  ",f1_score(test_labels, predicted, average='micro') )
    # print(classification_report(dataset.test.labels, preds))
    # print("F1_micor score on test =  ",f1_score(dataset.test.labels, preds, average='micro') )


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description=os.path.basename(__file__))
    arg_parser.add_argument('-input', required=True, help='[input] dataset dir path')
    arg_parser.add_argument('-model', required=False, help='[optional, input, output]'
                                                                                ' model file path')
    arg_parser.add_argument('-c', required=False, default='-2:2:5:10', help='[optional, param] C parameter')
    arg_parser.add_argument('-output', required=True, help='[output] output dir path')
    main(arg_parser.parse_args())
