# -*- coding: utf-8  -*-
import yaml

from . import instructions
from . import values
from .exceptions import ParserException


class Code():
    def __init__(self, func_name='', func_args=None, local_vars=None, ins=None):
        self.labels = {}
        self.local_vars = local_vars if local_vars is not None else []
        self.instructions = ins if ins is not None else []
        self.function_name = None
        self.argument_count = 0

    def get_var(self, idx):
        return self.local_vars[idx]

    @property
    def var_count(self):
        return len(self.local_vars)

    @property
    def ins_count(self):
        return len(self.instructions)

    def add_ins(self, i):
        self.instructions.append(i)

    def add_label(self, l, v):
        if l is None:
            return
        self.labels[l] = v


def _process_func(code, func):
    if not func or not isinstance(func, dict):
        raise ParserException('"func" not defined')
    code.function_name = func['name']
    _process_vars(code, func['args'], inc_arg_count=True)


def _process_vars(code, args, inc_arg_count=False):
    for arg in args:
        t = arg['type'].lower()
        if inc_arg_count:
            code.argument_count += 1
        code.local_vars.append(values.types[t]())
        l = arg.get('label', None)
        code.add_label(l, code.var_count - 1)


def _process_ins(code, ins):
    #pass1
    for ip, i in enumerate(ins):
        if isinstance(i, dict):
            l = i.pop('label', None)
            code.add_label(l, ip)
    #pass2
    for ip, i in enumerate(ins):
        if isinstance(i, str):
            code.add_ins(instructions.keywords[i.lower()]())
        elif isinstance(i, dict):
            kw, value = list(i.items())[0]
            ins_obj = instructions.keywords[kw.lower()]
            if issubclass(ins_obj, instructions.InsArgNumber):
                if isinstance(value, str):
                    value = code.labels[value]
            value = ins_obj.arg_class(value)
            code.add_ins(ins_obj(value))
        else:
            raise ParserException('unknown instruction format %s' % i)


def process_yaml(structure):
    c = Code()
    _process_func(c, structure.get('func', {}))
    _process_vars(c, structure.get('lvars', []))
    _process_ins(c, structure.get('ins', []))
    return c


def parse_string(data):
    structure = yaml.safe_load(data)
    return process_yaml(structure)


def parse_file(fname):
    with open(fname, 'r') as f:
        return parse_string(f)
