import json

json_file = './crawled_JRSSC/jrssc_12001.json'
with open(json_file) as json_data:
    content = json.load(json_data)

output_file = open("output_file.txt",'w')
output_file.write(content)
output_file.close()

process_file = open("output_file.txt")
lines = process_file.readlines()

last_end = -1
k = 0
for i in range(len(lines)):
    if '<section class=' in lines[i]:
        # print(i, line.strip())
        if '<h2>' in lines[i+1].strip():
            print(lines[i+2].strip())
            if last_end == -1:
                print("write")
            if last_end > 0:
                output_file = open(lines[last_end+2].strip()+'.txt','w')
                print("write")
                for line in lines[last_end:i]:
                    output_file.write(line)
                output_file.close()
            last_end = i


        elif '<h3>' in lines[i+1].strip():
            print('  '+lines[i+2].strip())
        
        
        
process_file.close()
