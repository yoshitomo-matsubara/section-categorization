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

    
def convert_to_label(preds):
    predicted = []
    # read_idx_list = []
    for i,line in enumerate(preds):
        pred_idx = np.argmax(line)
        predicted.append(pred_idx)
    return predicted

def generate_label_array(labels):
    Y = np.zeros([labels.shape[0],6])
    for i in range(len(labels)):
        if labels[i] == 'x':
            Y[i,0] = 1
        else:
            try:
                Y[i,int(labels[i])] = 1
            except:
                Y[i,0] = 1
                print(i, labels[i])
    return Y

def convert_str_to_label(str_y):
    int_y = []
    for i,label in enumerate(str_y):
        if label == 'x':
            int_y.append(0)
        else:
            int_y.append(int(label))
    return int_y   

def get_model(X,Y,input_shape,kernal_size, drop_out, n_layers):
    input_layer = tflearn.input_data(shape=[None, input_shape[1]])
    dense1 = tflearn.fully_connected(input_layer, kernal_size, activation='tanh',
                                    regularizer='L2', weight_decay=0.001)
    dropout1 = tflearn.dropout(dense1, drop_out)
    # increas layers
    for _ in range(n_layers-1):
        dropout1 = tflearn.dropout(dense1, drop_out)
        dense1 = tflearn.fully_connected(dropout1, 32, activation='tanh',
                                        regularizer='L2', weight_decay=0.001)
        dropout1 = tflearn.dropout(dense1, 0.8)

    softmax = tflearn.fully_connected(dropout1, 6, activation='softmax')
    # Regression using SGD with learning rate decay and Top-3 accuracy
    sgd = tflearn.SGD(learning_rate=0.1, lr_decay=0.96, decay_step=1000)
    # top_k = tflearn.metrics.Top_k(3)
    net = tflearn.regression(softmax, optimizer=sgd, loss='categorical_crossentropy')
    # Training
    model = tflearn.DNN(net, tensorboard_verbose=0)

    # model.fit(X, Y, n_epoch=20, validation_set=(validationX, validationY), show_metric=True, run_id="dense_model")
    model.fit(X, Y, n_epoch=20, show_metric=False)
    return model

def DNN(args, dataset):
    # Classification
    input_shape = dataset.training.feature_mat.shape
    Y = generate_label_array(dataset.training.labels)
    X = dataset.training.feature_mat
    testY = convert_str_to_label(dataset.validation.labels)

    best_valid_acc = -np.inf
    best_model = None
    best_layers = 0
    for kernal_size in [4,8,16,32]:
        for drop_out in [0.2,0.4,0.6,0.8]:
            for layers in [1,2,3]:
                with tf.Graph().as_default():  
                    validationX = dataset.validation.feature_mat
                    validationY = generate_label_array(dataset.validation.labels)
                    model = get_model(X,Y,input_shape,kernal_size,drop_out,layers)      # get model
                    preds = model.predict(validationX)
                    predicted = convert_to_label(preds)
                    valid_acc = accuracy_score(testY, predicted)
                    print(kernal_size, drop_out, layers, valid_acc)
                    if valid_acc > best_valid_acc:
                        best_valid_acc = valid_acc
                        best_model = model
                        best_kernal_size = kernal_size
                        best_drop_out = drop_out
                        best_layers = layers
    print('Best validation accuracy:', best_valid_acc, 'Best kernal size:', best_kernal_size,' Best drop out:', best_drop_out, ' best layer: ',best_layers)
    return best_model


def main(args):
    dataset = experiment_util.Dataset(args.input)
    model = experiment_util.load_model(args.model)
    if model is None:    
        model = DNN(args, dataset)
        if args.model is not None:
            experiment_util.save_model(model, args.model)
    preds = model.predict(dataset.test.feature_mat)
    predicted = convert_to_label(preds)
    test_labels = convert_str_to_label(dataset.test.labels)
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
