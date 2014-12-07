# -*- coding: utf-8  -*-
import os
import sys
import argparse

if sys.version_info < (3, 0):
    raise Exception('need Python 3k to run')

from TSBVMIP import engine


# just to be sure, exit if not run as main
if __name__ != '__main__':
    print('supposed to be run from console as command')
    exit()


m = engine.VM()

# load code file argument first and check if it exists
parser = argparse.ArgumentParser()
parser.add_argument('codefile', help='File path containing code you want to run')
args, unknown = parser.parse_known_args()
file_path = args.codefile
if not os.path.exists(file_path):
    print('file %s does not exists' % file_path)

# load the actual code
m.load_file_code(file_path)

# depending on the arguments in the function in the code, prepare command line arguments
for i, lvt in enumerate(m.args_types):
    name = '--arg%d' % i
    if isinstance(lvt, engine.INT):
        parser.add_argument(name, type=int, required=True, help='integer value')
    elif isinstance(lvt, engine.INTARRAY):
        parser.add_argument(name, type=int, nargs='+', required=True, help='integer values, will be packed to an array')
    elif isinstance(lvt, engine.FLOAT):
        parser.add_argument(name, type=float, required=True, help='float value')
    elif isinstance(lvt, engine.FLOATARRAY):
        parser.add_argument(name, type=float, nargs='+', required=True, help='float values, will be packed to an array')
args = parser.parse_args()

# arguments parsed ok, convert to list to pass for converting to TSBVMIP values and further
pargs = []
for i, _ in enumerate(m.args_types):
    name = 'arg%d' % i
    pargs.append(vars(args)[name])

cargs = m.convert_args(pargs)

# and now run with ready arguments
print('RETURN', m.run(*cargs))
