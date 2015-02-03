# -*- coding: utf-8  -*-
import os
import sys
import argparse

if sys.version_info < (3, 0):
    raise Exception('need Python 3k to run')

from TSBVMIP import engine
from TSBVMIP import value_types


# just to be sure, exit if not run as main
if __name__ != '__main__':
    print('supposed to be run from console as command')
    exit()


m = engine.VM()

# load code file argument first and check if it exists
parser = argparse.ArgumentParser()
parser.add_argument(
    'codefile', help='File path containing code you want to run')
args, unknown = parser.parse_known_args()
file_path = args.codefile
if not os.path.exists(file_path):
    print('file %s does not exists' % file_path)

# load the actual code
m.load_file_code(file_path)

# depending on the arguments in the function in the code, prepare command
# line arguments
for i, lvt in enumerate(m.args_types):
    name = '--arg%d' % i
    if lvt == value_types.INT:
        parser.add_argument(name, type=int, required=True,
                            help='integer value')
    elif lvt == value_types.INT_ARRAY:
        parser.add_argument(name, type=int, nargs='+', required=True,
                            help='integer values, will be packed to an array')
    elif lvt == value_types.FLOAT:
        parser.add_argument(name, type=float, required=True,
                            help='float value')
    elif lvt == value_types.FLOAT_ARRAY:
        parser.add_argument(name, type=float, nargs='+', required=True,
                            help='float values, will be packed to an array')
    else:
        raise Exception('unknown type %s to add as parameter' % lvt)
args = parser.parse_args()

# arguments parsed ok, run
print('RETURN', m.run_cmd(args))
