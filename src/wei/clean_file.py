import requests
import re
import json


import urllib.request

file_name = "1 Introduction.txt"

with open(file_name,'r') as f:
	raw_text = f.read()

a = re.sub(r'<.+>\n',r' ', raw_text)

with open("newtext.txt",'w') as f:
	json.dump(a,f)



