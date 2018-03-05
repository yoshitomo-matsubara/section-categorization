import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from scipy.sparse import hstack

class_names = ['1', '2', '3', '4', '5', 'a']

train = pd.read_csv('../section_train.csv',error_bad_lines=False).fillna(' ')
test = pd.read_csv('../section_test.csv',error_bad_lines=False).fillna(' ')
submission = pd.read_csv('./test.csv',error_bad_lines=False).fillna(' ')


rate = {'a':0,1:0,2:0,3:0,4:0,5:0}
count = 0
for i in range(len(test)):
    test_label = -1
    submission_label = -1
    sub_max = -1
    for label in [1,2,3,4,5,'a']:
        if test.iloc[i][label] == 1:
            test_label = label
        if submission.iloc[i][label] > sub_max:
            sub_max = submission.iloc[i][label]
            submission_label = label
    sub_list = [submission.iloc[i][label] for label in [1,2,3,4,5,'a']]
    if test_label != submission_label:
        count += 1
        rate[test_label] += 1

print(count/len(test))
print(rate)