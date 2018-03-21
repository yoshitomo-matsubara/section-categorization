import os
import numpy as np


import scipy.sparse as sp
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
def file_process(path, filename):
    X= []
    label = []
    global file_num # number of files
    file_num = 0 # number of sections
    global sect_num
    sect_num = 0
    for i in range(len(filename)):
        subfile = os.listdir(os.path.join(path,filename[i]))
        file_num += 1
        for j in range(len(subfile)):
            if subfile[j][0] == 'a':
                continue
            with open(os.path.join(path,filename[i],subfile[j]),'r') as f:
                      content_lines = f.readlines()
                      label.append(subfile[j][0])
                      X.append(content_lines[1])
                      sect_num +=1
    return X, label

### Used to grab extra features from the first line of each section
def get_new_feat(path, filename):
    newfeat = []
    for i in range(len(filename)):
        subfile = os.listdir(os.path.join(path,filename[i]))
        for j in range(len(subfile)):
            if subfile[j][0] == 'a':
                continue
            with open(os.path.join(path,filename[i],subfile[j]),'r') as f:
                content_lines = f.readlines()[0]
                feat = [int(t) for t in content_lines.split() if t.isdigit()]
                feat = feat[-5:]
                newfeat.append(feat)
    return newfeat   

## get training set
filename = os.listdir("./phy_split_data/training/raw")
path = "./phy_split_data/training/raw"
data_train, y_train = file_process(path, filename)
data_train_newfeat = get_new_feat(path, filename)

print('training data is loaded...')
print('file is: ',file_num, '\t section is:', sect_num)


## get validation set
filename = os.listdir("./phy_split_data/validation/raw")
path = "./phy_split_data/validation/raw"
data_dev, y_dev = file_process(path, filename)
data_dev_newfeat = get_new_feat(path, filename)

print('dev data is loaded...')
print('file is: ',file_num, '\t section is:', sect_num)


## get test set
filename = os.listdir("./phy_split_data/test/raw")
path = "./phy_split_data/test/raw"
data_test, y_test = file_process(path, filename)
data_test_newfeat = get_new_feat(path, filename)

print('test data is loaded...')
print('file is: ',file_num, '\t section is:', sect_num)



### get feature vector


word_vectorizer = CountVectorizer(max_features=1000)

## physics: max_features=1000
## cs: max_features= 2100
## stat: max_features=1300
X_train =  word_vectorizer.fit_transform(data_train)
X_dev = word_vectorizer.transform(data_dev)
X_test = word_vectorizer.transform(data_test)

newfeat_train = np.array(data_train_newfeat)
newfeat_dev = np.array(data_dev_newfeat)
newfeat_test = np.array(data_test_newfeat)


full_X_train = sp.hstack((X_train,newfeat_train))
full_X_dev = sp.hstack((X_dev,newfeat_dev))
full_X_test = sp.hstack((X_test,newfeat_test))


### start fit model
from sklearn.naive_bayes import MultinomialNB
clf = MultinomialNB()
clf.fit(full_X_train, y_train)
y_pred_dev = clf.predict(full_X_dev)
y_pred_test = clf.predict(full_X_test)

#print(X_train.shape, X_test.shape)
##  print accuracy

target_names = ['1','2','3','4','5','x']
print(len(set(y_dev)))
print('accuracy on dev = ',accuracy_score(y_dev, y_pred_dev))
print('accuracy on test = ',accuracy_score(y_test, y_pred_test))
print(classification_report(y_dev,y_pred_dev,target_names=target_names))


##  print F_1 score micro
print('F1_micor score on dev = ', f1_score(y_dev, y_pred_dev, average='micro'))
print('F1_micor score on test = ', f1_score(y_test, y_pred_test, average='micro'))
print(classification_report(y_test, y_pred_test,target_names=target_names))


