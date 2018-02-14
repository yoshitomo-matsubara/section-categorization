import os
import re
file_name = './JRSSB_section/jrssb_12000'

files = os.listdir(file_name)

print(files[0])

with open(file_name + '/'+ files[2],'r') as f:
	content = f.read()



"""
a = re.sub(r'<.+>',r'', content)


with open('output_file.txt','w') as f:
	f.write(a)

with open('output_file.txt','r') as f:
	content = f.read()
"""
#print(content)
def clean(content):
	pattern1 = r"link__reference"
	idx = [(m.start(0), m.end(0)) for m in re.finditer(pattern1,content)]
	for m in re.finditer(pattern1,content):
		print(content[m.start(0):m.end(0)])
	#print(len(idx)/2)
	return len(idx)/2


#:        "references:#

rel=r'\"references:#.{1,30}\" title'
ref_all = re.findall(rel, content)
ref_id = [i[13:-7] for i in ref_all]

diff_id = len(set(ref_id))


a = re.sub(r'<.+>',r'', content)
a = ' '.join(a.split())


section_order = a[0]
print('a[0] = ', a[0])
#first_line  = 'reference  number is {}\n'.format(num)

#print(a)
for i in range(1,10):
	if str(a[0])+'.'+str(i) not in a:
		break

sub_number = i-1
print('subsection number is ', i-1)

first_line = files[2][0] + '\t' + files[2][2:-4] +' '+str(sub_number)+ '\t' + ','.join(ref_id)+ ' ' + str(diff_id)
print(first_line)




with open('output_file.txt','w') as f:
	f.write(first_line+'\n' + a)


