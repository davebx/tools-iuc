#!/usr/bin/env python
# Dan Blankenberg
from __future__ import print_function

import optparse
import os
import subprocess
import sys
from json import dumps, loads

DEFAULT_DATA_TABLE_NAMES = ["blastn_databases"]


def build_blastn_index(data_manager_dict, fasta_filename, params, target_directory, dbkey, sequence_id, sequence_name, data_table_names=DEFAULT_DATA_TABLE_NAMES):
    # TODO: allow multiple FASTA input files
    fasta_base_name = os.path.split(fasta_filename)[-1]
    sym_linked_fasta_filename = os.path.join(target_directory, fasta_base_name)
    os.symlink(fasta_filename, sym_linked_fasta_filename)
    args = ['makeblastdb', '-in', sym_linked_fasta_filename, '-dbtype', 'nucl', '-out', sequence_id]
    proc = subprocess.Popen(args=args, shell=False, cwd=target_directory)
    return_code = proc.wait()
    if return_code:
        print("Error building index.", file=sys.stderr)
        sys.exit(return_code)
    data_table_entry = dict(value=sequence_id, dbkey=dbkey, name=sequence_name, path=sequence_id)
    for data_table_name in data_table_names:
        _add_data_table_entry(data_manager_dict, data_table_name, data_table_entry)


def _add_data_table_entry(data_manager_dict, data_table_name, data_table_entry):
    data_manager_dict['data_tables'] = data_manager_dict.get('data_tables', {})
    data_manager_dict['data_tables'][data_table_name] = data_manager_dict['data_tables'].get(data_table_name, [])
    data_manager_dict['data_tables'][data_table_name].append(data_table_entry)
    return data_manager_dict


def main():
    parser = optparse.OptionParser()
    parser.add_option('-i', '--input', dest='input', action='store', type="string", default=None, help='Input FASTA')
    parser.add_option('-d', '--dbkey', dest='dbkey', action='store', type="string", default=None, help='Unique identifier')
    parser.add_option('-n', '--name', dest='name', action='store', type="string", default=None, help='Name')
    (options, args) = parser.parse_args()

    filename = args[0]

    params = loads(open(filename).read())
    #raise NameError(dumps(params, indent=2, sort_keys=True))
    target_directory = params['output_data'][0]['extra_files_path']
    os.mkdir(target_directory)
    data_manager_dict = {}

    if options.dbkey in [None, '', '?']:
        raise Exception('"%s" is not a valid dbkey. You must specify a valid dbkey.' % (options.dbkey))

    sequence_id, sequence_name = (options.dbkey, options.name)

    # build the index
    build_blastn_index(data_manager_dict, options.input, params, target_directory, options.dbkey, sequence_id, sequence_name, data_table_names=['blastn_databases'])

    # save info to json file
    open(filename, 'wb').write(dumps(data_manager_dict))


if __name__ == "__main__":
    main()
