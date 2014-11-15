#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import argparse

home_dir = os.path.abspath(os.path.expanduser('~'))
default_out_folder = os.path.join(home_dir, '.openvpn')
default_in_conf = os.path.join(home_dir, 'Downloads', 'client.ovpn')
default_out_conf = os.path.join(default_out_folder, 'client.ovpn')

default_tags_map = dict()
default_tags_map.update(ca=dict(start_tag="<ca>", end_tag="</ca>", extension='pem'))
default_tags_map.update(cert=dict(start_tag="<cert>", end_tag="</cert>", extension='pem'))
default_tags_map.update({
    'tls-auth': dict(start_tag="<tls-auth>", end_tag="</tls-auth>", extension='key')
})
default_tags_map.update(key=dict(start_tag="<key>", end_tag="</key>", extension='pem'))
# start_tagstart='<'
# start_tagend='</'
# end_tag='>'
# cacert_tag='ca'
# usercert_tag='cert'
# priv_key='key'
# tls_auth='tls-auth'


def read_data_from_fpath(fpath):
    fd = open(fpath, 'rb')
    result = fd.read()
    fd.close()
    return result


def write_data_to_fpath(data, fpath):
    if not len(data):
        print("Warning: file {} will be created empty!")
    fd = open(fpath, 'wb')
    fd.write(data)
    fd.close()


def gen_fpath_name(out_dir, fname, extension="pem"):
    f = ".".join([fname, extension])
    fpath = os.path.join(out_dir, f)
    return fpath


def ensure_out_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)


def get_tag_range_safe(lines, start_tag, end_tag):
    start_idx = -1
    end_idx = -1
    for idx, l in enumerate(lines):
        if l == start_tag:
            if -1 != start_idx:
                msg = "Tag: {start_tag} appears at: {start_idx}, {idx}".format(**locals())
                raise ValueError(msg)
            start_idx = idx
            continue

        if l == end_tag:
            if -1 != end_idx:
                msg = "Tag: {end_tag} appears at: {end_idx}, {idx}".format(**locals())
                raise ValueError(msg)
            end_idx = idx
            ## if the additional end tag idx occurs - it's the problem of the next call
            ## thus also don't need to check start_idx >= end_idx
            break

    if -1 == start_idx or -1 == end_idx:
        msg = " ".join([
            "error processing",
            start_tag + ".",
            "illegal range:",
            "=".join(["start_idx", str(start_idx)]),
            "is not before",
            "=".join(["end_idx", str(end_idx)]),
        ])
        raise ValueError(msg)

    return start_idx, end_idx


# def get_tag_value(lines, **kwargs):
#     assert isinstance(lines, (list, tuple,)) is True
#     assert len(lines) > 0
#     for k in ["start_tag", "end_tag"]:
#         assert k in kwargs, "Required key: {k} is missing".format(**locals())
#
#     start_tag = kwargs.get("start_tag")
#     end_tag = kwargs.get("end_tag")
#     start_idx, end_idx = get_tag_range_safe(lines, start_tag, end_tag)
#     return lines[start_idx+1:end_idx]


def parse_args(args):
    summary = "OpenVPN AS config file to free openvpn config file converter"
    parser = argparse.ArgumentParser(summary)
    parser.add_argument("-i", "--in_conf",
                        help="input file", default=default_in_conf)
    parser.add_argument("-o", "--out_conf",
                        help="output file", default=default_out_conf)
    parser.add_argument("-f", "--out_folder",
                        help="output folder", default=default_out_folder)
    return parser.parse_args(args=args)


def write_files_from_data_list(data_lines, split_files_data):
    assert isinstance(data_lines, (list, tuple))
    assert isinstance(split_files_data, (list, tuple))
    for item in split_files_data:
        path = item.get("path")
        data_arr = data_lines[item.get("start_idx")+1:item.get("end_idx")]
        data = "\n".join(data_arr) + "\n"
        write_data_to_fpath(data, path)


def extract_tags_data_into_write_list(data_lines, out_folder):
    result = []
    for k, v in default_tags_map.items():
        start_idx, end_idx = get_tag_range_safe(
            data_lines,
            v.get("start_tag"),
            v.get("end_tag")
        )
        path = gen_fpath_name(out_folder, k, extension=v.get('extension'))
        result.append(dict(
            path=path,
            start_idx=start_idx,
            end_idx=end_idx
        ))
    return result


def build_out_file_arr(data_lines, split_files_data):
    result = []
    curr = 0
    idx_list = []
    for i in split_files_data:
        idx_list.append((i["start_idx"], i["end_idx"],))
    idx_list.sort()
    for couple in idx_list:
        chunk = data_lines[curr:couple[0]]
        result.extend(chunk)
        curr = couple[1] + 1
    ## latest chunk:
    result.extend(data_lines[idx_list[-1][1]+1:-1])
    ## add the data for those files
    for item in split_files_data:
        path = item.get('path')
        kwd = os.path.basename(path).split('.')[0]
        l = " ".join([kwd, path])
        result.append(l)
    return "\n".join(result) + "\n"


def main():
    args = parse_args(sys.argv[1:])
    in_conf_file_name = args.in_conf
    out_conf_file_name = args.out_conf
    out_folder = args.out_folder

    data = read_data_from_fpath(in_conf_file_name)
    data_lines = data.split('\n')
    split_files_data = extract_tags_data_into_write_list(data_lines, out_folder)
    ensure_out_dir(out_folder)
    write_files_from_data_list(data_lines, split_files_data)
    out_file_data = build_out_file_arr(data_lines, split_files_data)
    write_data_to_fpath(out_file_data, out_conf_file_name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
