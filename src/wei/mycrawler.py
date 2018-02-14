from lxml import html
from bs4 import BeautifulSoup
import requests
import re
import json

import urllib.request

def write_json(content,num):
	with open('./crawled_JRSSB/jrssb_{}.json'.format(num),'w') as f:
		json.dump(content,f)

if __name__ == '__main__':
	

	for i in range(12260,12261):
		# JRSSB
		url = "http://onlinelibrary.wiley.com/doi/10.1111/rssb"+"."+str(i)+"/full"
		# JRSSC
		#url = "http://onlinelibrary.wiley.com/doi/10.1111/rssc"+"."+str(i)+"/full"
		try:
			r = urllib.request.urlopen(url)
		except:
			r = False
		if not r:
			continue
		page = r.read().decode('ascii', 'ignore')
		soup = BeautifulSoup(page,"lxml")
		content = soup.prettify()
		print(content)
		#write_json(content, i)
	