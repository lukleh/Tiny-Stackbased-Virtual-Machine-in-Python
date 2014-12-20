# -*- coding: utf8 -*-

import argparse
import os

from TSBVMIP import yparser
from TSBVMIP.analysis import analyzer

# load code file argument first and check if it exists
parser = argparse.ArgumentParser()
parser.add_argument('codefile', help='File path containing code you want to run')
args, unknown = parser.parse_known_args()
file_path = args.codefile
if not os.path.exists(file_path):
    print('file %s does not exists' % file_path)

# load the actual code
code = yparser.parse_file(file_path)

anz = analyzer.Analyzer()
anz.analyze_control(code)
print(anz.basic_blocks)