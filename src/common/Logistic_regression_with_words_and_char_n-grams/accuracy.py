import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from scipy.sparse import hstack

class_names = ['a', '1', '2', '3', '4', '5']

train = pd.read_csv('../section_train.csv',error_bad_lines=False).fillna(' ')
test = pd.read_csv('../section_test.csv',error_bad_lines=False).fillna(' ')
submission = pd.read_csv('./test_prob.csv',error_bad_lines=False).fillna(' ')


y_true = np.array(pd.DataFrame(test, columns=class_names))
submission_preds = np.zeros_like(y_true)

class_table = dict()
for c in class_names:
    class_table[c] = {'a':0,'1':0,'2':0,'3':0,'4':0,'5':0}

count = 0
for i in range(len(test)):
    test_label = -1
    submission_label = -1
    sub_max = -1
    for label in class_names:
        if test.iloc[i][label] == 1:
            test_label = label
        if submission.iloc[i][label] > sub_max:
            sub_max = submission.iloc[i][label]
            submission_label = label
            label_index = class_names.index(label)
    submission_preds[i,label_index] = 1
    class_table[submission_label][test_label] += 1

valid_acc = accuracy_score(y_true, submission_preds)
print("valid_acc", valid_acc)

class_table_DataFrame = pd.DataFrame(class_table)
print(class_table_DataFrame)
