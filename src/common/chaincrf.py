import argparse
import numpy as np
import os
from sklearn_crfsuite import CRF
from sklearn_crfsuite import metrics
from util import experiment_util
from pdb import set_trace as st


from pystruct.models import ChainCRF
from pystruct.learners import FrankWolfeSSVM
from sklearn.metrics import f1_score


def preprocess_feature(feat):
	# make each entry in feature matrix is integer
	for i in range(len(feat)):
		feat[i] = feat[i].astype(int)
	return feat

def preprocess_label(labels):
	# labels are ranged in [1,2,3,4,5,6]
	# Then process them ranged in [0,1,2,3,4,5]
	# this operation is required for chainCRF func since it labels from 0
	labels_array = labels
	for i in range(len(labels)):
		for j in range(len(labels[i])):
			if labels[i][j] =='x':
				labels_array[i][j] = 5
			elif labels[i][j].isdigit():
				labels_array[i][j] = int(labels[i][j])-1
			else:
				print('find some wired label...',i,j)
	labels_array = np.array([np.array(i)for i in labels_array])
	return labels_array

def restore_label(labels):
	# put preprocessed labels to original labels
	label_origin = []
	for i in range(len(labels)):
		row = []
		for j in range(len(labels[i])):
			if labels[i][j] == 5:
				row.append('x')
			else:
				row.append(str(labels[i][j]+1))
		label_origin.append(row)
	return label_origin


def get_one_list(labels):
	# used to get F_1 score
	label_list = []
	for i in range(len(labels)):
		for j in range(len(labels[i])):
			if labels[i][j] == 5:
				label_list.append('x')
			else:
				label_list.append(str(labels[i][j]+1))
	return label_list


filename = './task2-dataset/physics'
dataset = experiment_util.PaperDataset(filename, use_matrix=True)

x_train = dataset.training.feature_mats
x_train = preprocess_feature(x_train)
x_test = dataset.test.feature_mats
x_test = preprocess_feature(x_test)



y_train = dataset.training.list_of_labels
y_train = preprocess_label(y_train)
y_test = dataset.test.list_of_labels
y_test = preprocess_label(y_test)


### CS : best c =0.01
### Phy: best c= 0.005
### stat: best c = 0.005
'''
C= [0.005,0.01,0.02,0.05,0.1,0.2]
score = {}

for i in C:
	model = ChainCRF()
	ssvm = FrankWolfeSSVM(model=model, C=i, max_iter=100)
	ssvm.fit(x_train, y_train) 
	score[i] = ssvm.score(x_dev, y_dev)

print score
'''
model = ChainCRF()
ssvm = FrankWolfeSSVM(model=model, C=0.005, max_iter=100)
ssvm.fit(x_train, y_train)
score = ssvm.score(x_test, y_test)
y_pred = ssvm.predict(x_test)

print 'Micro-averaged F1 score:', f1_score(get_one_list(y_test), get_one_list(y_pred), average='micro')

experiment_util.sequential_error_analysis(restore_label(y_test),restore_label(y_pred),'./chaincrf_sequential_error_analysis')
