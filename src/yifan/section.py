from os import listdir, mkdir
from os.path import isfile, join
import re
from shutil import copyfile

intro = ["intro"]
related_work = ["related","background"]
approach = ["approach"]
experiment = ["experiment"]
result = ["result"]
conclusion = ["conclusion","discussion"]

section_categery = dict({"abstract":["abstract"],"intro":["intro"],
"related_work":["related","background"],
"approach":["approach","method","use","algorithm","setup","equation","model","equation","equation","problem"],
"experiment":["experiment","simulation","computational","numerical"],
"result":["result","discussion"],
"conclusion":["conclusion","outlook"]})


def process_paper(dirname, target_dir):
    """
    find section of crawled data
    """
    mypath = dirname
    # onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    papers = [f for f in listdir(mypath)]
    for paper in papers:
        if isfile(join(mypath, paper)):
            continue
        # print(paper)
        # filepath = mypath + '/' + file
        paperpath = dirname + '/' + paper
        target_paper_dir = target_dir + '/' + paper
        # print(file)
        assign_sections(dirname, paperpath, target_paper_dir)
        # try:
        #     process_using_h5(filepath, target_dir, file)
        # except:
        #     pass
            # print(filepath)
    return

def assign_sections(dirname, paperpath, target_dir):
    """
    """
    mkdir(target_dir)
    original_sections = target_dir+"/"+"original"
    mkdir(target_dir+"/"+"original")
    onlysections = [f for f in listdir(paperpath) if isfile(join(paperpath, f))]
    # papers = [f for f in listdir(paperpath)]
    content_dict = dict()
    for section in onlysections:
        if section.startswith("."):
            continue
        # print(section)
        sectionpath = paperpath + '/' + section
        copyfile(sectionpath, original_sections + '/' + section)
        with open(sectionpath) as file:  
            # section_content = file.read() 
            # section_content_lines = file.readlines() 
            section_content = file.read() 
        section_real_id = ""
        # section_signatures = section_content_lines[0]
        # print(section_signatures)
        # print(section_title.lower())
        section_keywords = section[0:-4].split("_")
        section_keywords = [word for word in section_keywords if len(word) > 1]
        # print(section_keywords)
        for cat in section_categery:
        #     # print(cat, " ", section_title.lower())
            for word in section_categery[cat]: 
                for keyword in section_keywords: 
                    # print(word, keyword)
                    if (keyword.lower() in word) or (word in keyword.lower()):
                        print(True, word, keyword)
                        section_real_id = cat
                        if cat in content_dict:
                            content_dict[cat] += section_content + "\n"
                        else:
                            content_dict[cat] = section_content + "\n"
                        break
        if section_real_id != "":
            # print(section_real_id)
            pass
        else:
            section_real_id = "others"
            if "others" in content_dict:
                content_dict["others"] += section_content + "\n"
            else:
                content_dict["others"] = section_content + "\n"
    print()    
    for cat in content_dict:
        f = open(target_dir + '/' + cat + ".txt",'w')
        f.write(content_dict[cat])
        f.close()
    return     


def process_using_h5(filepath, directory, paper_name):
    """
    """
    file = open(filepath)
    content = file.read()
    dst = directory + "/" + paper_name[0:-4]
    mkdir(dst)
    src = filepath
    # dst_original = dst + "/original_" + paper_name
    dst_original = dst + "/" + paper_name
    copyfile(src, dst_original)
    pattern = r"\"title_header\":\"h5\""
    idx = [(m.start(0), m.end(0)) for m in re.finditer(pattern, content)]
    last_end = 0
    letters = ["I","II","III","IV","V","VI","VII","VII","IX","X"]
    labeled_content = dict()
    for i in range(len(idx)):
        # print(idx[i])
        # label_order = "\"{}\"".format(letters[i])
        label_order = letters[i]
        section = content[last_end:idx[i][0]-2]
        section_idx = 1
        while(section[-section_idx].isupper() or section[-section_idx] == " "):
            section_idx += 1
        # print(letters[i]+" "+section[-section_idx+2:])
        if section_idx <= 2:
            continue
        section_title = section[-section_idx+1:]
        section_real_id = ""
        # print(section_title.lower())
        for cat in section_categery:
            # print(cat, " ", section_title.lower())
            for word in section_categery[cat]:                
                if (section_title.lower() in word) or (word in section_title.lower()):
                    section_real_id = cat
        if section_real_id != "":
            # print(section_real_id)
            pass
        else:
            section_real_id = "others"
        
        section_name = letters[i]+" "+section_title
        section_filename = directory + "/" + paper_name[0:-4] + "/" +  section_name + ".txt"
        section_text = section[0:-section_idx]
        if section_real_id not in labeled_content:
            labeled_content[section_real_id] = []
        labeled_content[section_real_id].append([section_title, section_text])
        # f = open(section_filename, "w")
        # f.write(section_text)
        # f.close()      
        last_end = idx[i][1]
        if i > 9:
            break
    for label in labeled_content:
        print("label",label)
        label_filename = directory + "/" + paper_name[0:-4] + "/" +  label + ".txt"
        f = open(label_filename, "w")
        for item in labeled_content[label]:
            f.write(item[0]+"\n")
            f.write(item[1]+"\n")
        f.close()    

if __name__ == "__main__":

    dir_path = "/Users/yifantian/Desktop/Course/CS295 NLP/Project/physics/cleaned-text"
    target_dir = "/Users/yifantian/Desktop/Course/CS295 NLP/Project/physics/processed"
    process_paper(dir_path, target_dir)