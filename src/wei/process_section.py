import json
import os


def open_json(file_name):
    with open(file_name) as json_data:
        content = json.load(json_data)
    return content


files = os.listdir("./crawled_JRSSB")


for file_name in files:
    print(file_name)
    content = open_json("./crawled_JRSSB"+"/"+file_name)
    output_file = open("output_file.txt",'w')
    output_file.write(content)
    output_file.close()


    dir_path = os.path.join("JRSSB_section", file_name[:-5])  # will return 'feed/address'
    os.makedirs(dir_path)  

    process_file = open("output_file.txt")
    lines = process_file.readlines()



    last_end = -1
    j = 0
    for i in range(len(lines)):

        if '<h2 class="article-section__header">' in lines[i]:
            last_end = i
            print(last_end)
            continue
        
        if '<section class=' in lines[i]:
            # print(i, line.strip())

            if '<h2>' in lines[i+1].strip():
                #print(lines[i+2].strip())
                #if last_end == -1:
                    #pass
                    #print("write")
                if last_end > 0:
                    if j ==0:
                        output_file = open(dir_path+'/'+lines[last_end+1].strip()+'.txt','w')
                        j=1
                    else:
                        output_file = open(dir_path+'/'+lines[last_end+2].strip()+'.txt','w')
                    for line in lines[last_end:i]:
                        output_file.write(line)
                    output_file.close()
                last_end = i
                #print(last_end)


            elif '<h3>' in lines[i+1].strip():
                #print('  '+lines[i+2].strip())
                pass
             
     
