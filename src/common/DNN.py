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
from sklearn import metrics
    
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

# def get_model(X,Y,input_shape, kernal_size, drop_out, n_layers):
def get_model(X,Y,input_shape, kernal_size, drop_out, activation):
    n_layers = 2
    input_layer = tflearn.input_data(shape=[None, input_shape[1]])
    input_layer = tflearn.dropout(input_layer, drop_out)
    dense1 = tflearn.fully_connected(input_layer, kernal_size, activation=activation)
    dense1 = tflearn.dropout(dense1, drop_out)
    # increas layers
    for _ in range(n_layers-1):
        # dropout1 = tflearn.dropout(dense1, drop_out)
        dense1 = tflearn.fully_connected(dense1, kernal_size, activation=activation)
        dropout1 = tflearn.dropout(dense1, 0.8)

    softmax = tflearn.fully_connected(dense1, 6, activation='softmax')
    # Regression using SGD with learning rate decay and Top-3 accuracy
    sgd = tflearn.SGD(learning_rate=0.1, lr_decay=0.96, decay_step=1000)
    # top_k = tflearn.metrics.Top_k(3)
    net = tflearn.regression(softmax, optimizer=sgd, learning_rate=0.01, loss='categorical_crossentropy')
    # net = tflearn.regression(softmax, optimizer=sgd, learning_rate=0.01, loss='categorical_crossentropy')
    # Training adagrad
    model = tflearn.DNN(net, tensorboard_verbose=3, tensorboard_dir='./tmp/tflearn_logs/')
    # model.fit(X, Y, n_epoch=20, validation_set=(validationX, validationY), show_metric=True, run_id="dense_model")
    # model.fit(X, Y, n_epoch=20, show_metric=False)
    model.fit(X, Y)
    return model

def DNN_train(args, dataset):
    # Classification
    input_shape = dataset.training.feature_mat.shape
    Y = generate_label_array(dataset.training.labels)
    X = dataset.training.feature_mat
    testY = convert_str_to_label(dataset.validation.labels)
    # print(input_shape[1])
    # raise SystemExit(0)
    best_valid_acc = -np.inf
    best_model = None
    best_layers = 0
    best_activation = ''
    # for kernal_size in [16,32,64,128]:
    for kernal_size in [100,150,200]:
        for drop_out in [0.8,1.0]:
            # for layers in [1]:
            for activation in ['relu']:
                with tf.Graph().as_default():  
                    validationX = dataset.validation.feature_mat
                    validationY = generate_label_array(dataset.validation.labels)
                    model = get_model(X,Y,input_shape,kernal_size,drop_out,activation)      # get model
                    preds = model.predict(validationX)
                    predicted = convert_to_label(preds)
                    valid_acc = accuracy_score(testY, predicted)
                    print(kernal_size, drop_out, activation, valid_acc)
                    if valid_acc > best_valid_acc:
                        best_valid_acc = valid_acc
                        best_model = model
                        best_kernal_size = kernal_size
                        best_drop_out = drop_out
                        best_activation = activation
                        # best_layers = layers
    print('Best validation accuracy:', best_valid_acc, 'Best kernal size:', best_kernal_size,' Best drop out:', best_drop_out, ' best layer: ',best_activation)
    return best_model

def DNN_load(args):
    feat_dim = 6166   # 3918
    n_layers = 1
    input_layer = tflearn.input_data(shape=[None, feat_dim])
    dense1 = tflearn.fully_connected(input_layer, 64, activation='softplus',
                                    regularizer='L2', weight_decay=0.001)
    dropout1 = tflearn.dropout(dense1, 1,0)
    # increas layers
    for _ in range(n_layers-1):
        dropout1 = tflearn.dropout(dense1, 1.0)
        dense1 = tflearn.fully_connected(dropout1, 16, activation='softplus',
                                        regularizer='L2', weight_decay=0.001)
        dropout1 = tflearn.dropout(dense1, 0.8)

    softmax = tflearn.fully_connected(dropout1, 6, activation='softmax')
    # Regression using SGD with learning rate decay and Top-3 accuracy
    sgd = tflearn.SGD(learning_rate=0.1, lr_decay=0.96, decay_step=1000)
    # top_k = tflearn.metrics.Top_k(3)
    net = tflearn.regression(softmax, optimizer=sgd, loss='categorical_crossentropy')
    # Training
    model = tflearn.DNN(net, tensorboard_verbose=0)
    model.load(args.model)
    return model
    

def main(args):
    dataset = experiment_util.Dataset(args.input)
    if args.train == '1':
        model = DNN_train(args, dataset)
    elif args.train == '0':
        model = DNN_load(args)
    if args.model is not None:
        experiment_util.save_model(model, args.model)
    preds = model.predict(dataset.test.feature_mat)
    predicted = convert_to_label(preds)
    test_labels = convert_str_to_label(dataset.test.labels)
    
    print(classification_report(test_labels, predicted))
    print("F1_micor score on test =  ",f1_score(test_labels, predicted, average='micro') )
    print("Confusion Matrix:")
    print(metrics.confusion_matrix(test_labels, predicted))
    print('\n')
    experiment_util.error_analysis(dataset.test.labels, predicted, args.output)



if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description=os.path.basename(__file__))
    arg_parser.add_argument('-input', required=True, help='[input] dataset dir path')
    arg_parser.add_argument('-train', required=True, help='[input] dataset dir path')
    arg_parser.add_argument('-model', required=False, help='[optional, input, output]'
                                                                                ' model file path')
    arg_parser.add_argument('-c', required=False, default='-2:2:5:10', help='[optional, param] C parameter')
    arg_parser.add_argument('-output', required=True, help='[output] output dir path')
    main(arg_parser.parse_args())
