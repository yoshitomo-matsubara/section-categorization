import argparse
import os
import common


def get_file_path_list(input_dir_path):
    file_path_list = [os.path.join(input_dir_path, file_name) for file_name in os.listdir(input_dir_path)\
                      if os.path.isfile(os.path.join(input_dir_path, file_name))]
    return file_path_list


def read_doi_file(doi_file_path):
    doi_list = []
    with open(doi_file_path, 'r') as fp:
        for line in fp.readlines():
            if line != '\n':
                doi_list.append(line.strip())
    return doi_list


def download_text(doi_list, elsevier, is_raw, base_output_dir):
    http_accept = 'httpAccept=text/plain' if is_raw else 'httpAccept=text/xml'
    element = doi_list[0].split('/')[1]
    dir_name = element[element.find('.') + 1:element.find('.', 2)]
    output_dir_path = os.path.join(base_output_dir, dir_name)
    if not os.path.exists(output_dir_path):
        os.makedirs(output_dir_path)
    for doi in doi_list:
        file_name = doi.replace('/', '-').replace('.', '_') + '.xml'
        text = elsevier.text_request(doi, [http_accept])
        output_file_path = os.path.join(output_dir_path, file_name)
        with open(output_file_path, 'w') as fp:
            fp.write(text.decode("utf-8"))


def main(args):
    doi_file_path_list = get_file_path_list(args.input)
    elsevier = common.Elsevier()
    for doi_file_path in doi_file_path_list:
        doi_list = read_doi_file(doi_file_path)
        download_text(doi_list, elsevier, args.raw, args.output)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description=os.path.basename(__file__))
    arg_parser.add_argument('-input', required=True, help='[input] doi dir path')
    arg_parser.add_argument('-raw', action='store_true', help='[param, optional] download raw text')
    arg_parser.add_argument('-output', required=True, help='[output] output dir path')
    main(arg_parser.parse_args())
