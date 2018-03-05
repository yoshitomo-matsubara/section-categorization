from os import listdir, mkdir
from os.path import isfile, join
import re
from shutil import copyfile
import hashlib
import pandas as pd


def create_csv(mypath):
    """
    create csv file from dir
    """
    section_list = []
    onlyfiles = [f for f in listdir(mypath) if not isfile(join(mypath, f))]
    for file in onlyfiles:
        print(file)
        filepath = mypath + '/' + file
        files = [f for f in listdir(filepath) if isfile(join(filepath, f))]
        for file in files:
            title = file.split('-')
            if title[0].isdigit() or title[0] == 'a':
                with open(filepath+'/'+file) as f:
                    content = f.read()
                    lines = content.split('\n')
                fileId = filepath + title[1]
                fileId = hashlib.md5(fileId.encode()).hexdigest()
                sample = dict()
                for label in ['a','1','2','3','4','5']:
                    sample[label] = 0
                sample[title[0]] = 1
                sample['id'] = fileId
                sample['text'] = ' '.join(lines[1:])
                sample['meta'] = lines[0]
                section_list.append(sample)
    df = pd.DataFrame(section_list)
    return df


if __name__ == "__main__":
    mypath = './input/test/raw'
    df = create_csv(mypath)
    file_name = 'section_test.csv'
    df.to_csv(file_name)