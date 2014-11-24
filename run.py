# -*- coding: utf-8  -*-
import sys

if sys.version_info[0] != 3:
    raise Exception('need Python 3k to run')

from vm import engine

if __name__ == '__main__':
    m = engine.VM()
    fname = sys.argv[1]
    m.load_file_code(fname)
    cargs = m.convert_args(sys.argv[2:])
    print('RETURN', m.run(*cargs))
else:
    print('supposed to be run from console as command')