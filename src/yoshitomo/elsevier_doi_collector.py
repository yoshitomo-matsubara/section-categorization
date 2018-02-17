import argparse
import os
import urllib.parse
import json
import common


def read_file(file_path):
    value_list = []
    with open(file_path, 'r') as fp:
        for line in fp:
            if line != '\n':
                value_list.append(line.strip())
    return value_list


def extract_dois(result, journal_name):
    doi_set = set()
    json_dict = json.loads(result.decode("utf-8"))
    if 'search-results' not in json_dict:
        return None, 0
    entries = json_dict['search-results']['entry']
    for entry in entries:
        if entry['prism:publicationName'] == journal_name:
            doi_set.add(entry['prism:doi'])
    return doi_set, len(entries)


def collect_dois(journal_name, elsevier, output_dir_path, size=100, count=100):
    content = 'content=journals'
    key = 'SRCTITLE(' + journal_name + ')'
    encoded_key = 'query=' + str(urllib.parse.quote(key))
    count_str = 'count=' + str(count)
    doi_set = set()
    start_idx = 0
    while len(doi_set) < size:
        start_idx_str = 'start=' + str(start_idx)
        result = elsevier.search_request([start_idx_str, count_str, encoded_key, content])
        extracted_doi_set, entry_size = extract_dois(result, journal_name)
        if extracted_doi_set is None:
            print('\tNo more DOIs')
            break
        doi_set.update(extracted_doi_set)
        start_idx += entry_size

    file_name = journal_name.lower().replace(' ', '_').replace('&', 'and') + '.txt'
    with open(output_dir_path + file_name, 'w') as fp:
        for doi in doi_set:
            fp.write(doi + '\n')
    print('\tDownloaded', len(doi_set), '/', size)


def main(args):
    journal_names = read_file(args.input)
    elsevier = common.Elsevier()
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    for journal_name in journal_names:
        print(journal_name)
        collect_dois(journal_name, elsevier, args.output, size=args.size)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description=os.path.basename(__file__))
    arg_parser.add_argument('-input', required=True, help='[input] journal list file path')
    arg_parser.add_argument('-size', required=False, type=int, default=100, help='[input] number of DOIs to download')
    arg_parser.add_argument('-output', required=True, help='[output] output dir path')
    main(arg_parser.parse_args())
