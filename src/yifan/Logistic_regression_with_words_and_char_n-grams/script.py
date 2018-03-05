import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from scipy.sparse import hstack

class_names = ['1', '2', '3', '4', '5', 'a']

train = pd.read_csv('../section_train.csv',error_bad_lines=False).fillna(' ')
validation = pd.read_csv('../section_validation.csv',error_bad_lines=False).fillna(' ')
test = pd.read_csv('../section_test.csv',error_bad_lines=False).fillna(' ')


train_text = train['text']
validation_text = validation['text']
test_text = test['text']

all_text = pd.concat([train_text, test_text])

word_vectorizer = TfidfVectorizer(
    sublinear_tf=True,
    strip_accents='unicode',
    analyzer='word',
    token_pattern=r'\w{1,}',
    stop_words='english',
    ngram_range=(1, 1),
    max_features=10000)
word_vectorizer.fit(all_text)
train_word_features = word_vectorizer.transform(train_text)
validation_word_features = word_vectorizer.transform(validation_text)
test_word_features = word_vectorizer.transform(test_text)

char_vectorizer = TfidfVectorizer(
    sublinear_tf=True,
    strip_accents='unicode',
    analyzer='char',
    stop_words='english',
    ngram_range=(2, 6),
    max_features=50000)
char_vectorizer.fit(all_text)
train_char_features = char_vectorizer.transform(train_text)
validation_char_features = char_vectorizer.transform(validation_text)
test_char_features = char_vectorizer.transform(test_text)

train_features = hstack([train_char_features, train_word_features])
validation_features = hstack([validation_char_features, validation_word_features])
test_features = hstack([test_char_features, test_word_features])


submission = pd.DataFrame.from_dict({'id': test['id']})

scores = []
for class_name in class_names:
    train_target = train[class_name]
    classifier = LogisticRegression(solver='sag')

    # cv_score = np.mean(cross_val_score(classifier, train_features, train_target, cv=3, scoring='roc_auc'))
    # scores.append(cv_score)
    # print('CV score for class {} is {}'.format(class_name, cv_score))

    classifier.fit(train_features, train_target)
    submission[class_name] = classifier.predict_proba(test_features)[:, 1]
    # submission[class_name] = classifier.predict(test_features)[:, 1]

# print('Total CV score is {}'.format(np.mean(scores)))

# submission.to_csv('submission.csv', index=False)
# submission.to_csv('validation.csv', index=False)
submission.to_csv('test.csv', index = False)




