import argparse
import numpy as np
import os
from sklearn_crfsuite import CRF
from sklearn_crfsuite import metrics
from util import experiment_util
from pdb import set_trace as st

from pystruct.models import ChainCRF
from pystruct.learners import FrankWolfeSSVM



def preprocess_feature(feat):
	# make each entry in feature matrix is integer
	for i in range(len(feat)):
		feat[i] = feat[i].astype(int)
	return feat

def preprocess_label(labels):
	# labels are ranged in [1,2,3,4,5,6]
	# Then process them ranged in [0,1,2,3,4,5]
	# this operation is required for chainCRF func since it labels from 0
	for i in range(len(labels)):
		for j in range(len(labels[i])):
			if labels[i][j] =='x':
				labels[i][j] = 5
			elif labels[i][j].isdigit():
				labels[i][j] = int(labels[i][j])-1
			else:
				print('find some wired label...',i,j)
	labels = np.array([np.array(i)for i in labels])
	return labels

filename = './task2-dataset/physics'
dataset = experiment_util.PaperDataset(filename, use_matrix=True)

x_train = dataset.training.feature_mats
x_train = preprocess_feature(x_train)
x_dev = dataset.validation.feature_mats
x_dev = preprocess_feature(x_dev)



y_train = dataset.training.list_of_labels
y_train = preprocess_label(y_train)
y_dev = dataset.validation.list_of_labels
y_dev = preprocess_label(y_dev)


### CS : best c =0.01
### Phy: best c= 0.005
### stat: best c = 0.005
C= [0.005,0.01,0.02,0.05,0.1,0.2]
score = {}

for i in C:
	model = ChainCRF()
	ssvm = FrankWolfeSSVM(model=model, C=i, max_iter=100)
	ssvm.fit(x_train, y_train) 
	score[i] = ssvm.score(x_dev, y_dev)

print score


