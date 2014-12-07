# -*- coding: utf-8  -*-
import yaml

from . import instructions
from . import values
from .exceptions import ParserException


class Code():
    def __init__(self, func=None, lvars=[], ins=[]):
        self.labels = {}
        self.local_vars = []
        self.instructions = []
        self.function_name = None
        self.argument_count = 0

        self._process_func(func)
        self._process_vars(lvars)
        self._process_ins(ins)

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

    def _process_func(self, func):
        if not func or not isinstance(func, dict):
            raise ParserException('"func" not defined')
        self.function_name = func['name']
        self._process_vars(func['args'], inc_arg_count=True)

    def _process_vars(self, args, inc_arg_count=False):
        for arg in args:
            t = arg['type'].lower()
            if inc_arg_count:
                self.argument_count += 1
            self.local_vars.append(values.types[t]())
            l = arg.get('label', None)
            self.add_label(l, self.var_count - 1)

    def add_label(self, l, v):
        if l is None:
            return
        self.labels[l] = v

    def _process_ins(self, ins):
        #pass1
        for ip, i in enumerate(ins):
            if isinstance(i, dict):
                l = i.pop('label', None)
                self.add_label(l, ip)
        #pass2
        for ip, i in enumerate(ins):
            if isinstance(i, str):
                self.add_ins(instructions.keywords[i.lower()]())
            elif isinstance(i, dict):
                kw, value = list(i.items())[0]
                ins_obj = instructions.keywords[kw.lower()]
                if issubclass(ins_obj, instructions.InsArgNumber):
                    if isinstance(value, str):
                        value = self.labels[value]
                value = ins_obj.arg_class(value)
                self.add_ins(ins_obj(value))
            else:
                raise ParserException('unknown instruction format %s' % i)


def parse_string(data):
    structure = yaml.safe_load(data)
    return Code(**structure)


def parse_file(fname):
    with open(fname, 'r') as f:
        return parse_string(f)
