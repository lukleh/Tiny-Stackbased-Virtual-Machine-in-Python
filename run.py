# -*- coding: utf-8  -*-
import os
import sys

from vm import engine

if __name__ == '__main__':
    m = engine.VM()
    # m.load_file_code(os.path.join('test', 'fixtures', 'parse_ok.code'))
    fname = sys.argv[1]
    m.load_file_code(fname)
    cargs = m.convert_args(sys.argv[2:])
    print('RETURN', m.run(*cargs))
else:
    print('supposed to be run from console as command')