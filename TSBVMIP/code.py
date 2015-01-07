# -*- coding: utf-8  -*-

from .exceptions import ParserException


class Code():

    def __init__(self):
        self.labels = {}
        self.variables = []
        self.instructions = []
        self.function_name = None
        self.argument_count = 0
        self.return_type = None

    def get_var(self, idx):
        return self.variables[idx]

    @property
    def arguments(self):
        for i in range(self.argument_count):
            yield self.get_var(i)

    @property
    def local_variables(self):
        for i in range(self.argument_count, self.var_count):
            yield self.get_var(i)

    @property
    def var_count(self):
        return len(self.variables)

    @property
    def ins_count(self):
        return len(self.instructions)

    def add_ins(self, i):
        self.instructions.append(i)

    def add_label(self, l, v):
        if not isinstance(l, str):
            raise ParserException('label %s needs to be a string' % l)
        if l is None:
            raise ParserException('every local variable needs a label')
        if l in self.labels:
            raise ParserException('labels has to be unique: duplicate %s' % l)
        self.labels[l] = v
